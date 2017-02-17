"""
This module  takes care of all the changes for bigchain and votes.
"""

from multipipes import Pipeline, Node
from extend.localdb.pipelines.local_utils import ChangeFeed

from bigchaindb.db.utils import get_conn
import bigchaindb
from extend.localdb.leveldb import utils as ldb
import rethinkdb as r
import rapidjson
import datetime

import logging

db_name = bigchaindb.config['database']['name']

logger = logging.getLogger(__name__)


class LocalVote():
    """Monitor the vote changes and write to leveldb

    This class monitor the change for votes through changefeed
    and write the changes to localblock dir.

    Note:
        Methods of this class will be executed in different processes.
    """

    INSERT = 1
    DELETE = 2
    UPDATE = 4

    def __init__(self, current_vote_num=None, conn_vote=None, conn_vote_header=None):
        """Initialize the LocalVotePipeline creator"""
        self.conn_vote = conn_vote or ldb.LocalVote().conn['vote']
        self.conn_vote_header = conn_vote_header or ldb.LocalVote().conn['vote_header']
        self.current_vote_num = current_vote_num or int(ldb.get_withdefault(
            self.conn_vote_header, 'current_vote_num', '0'))
        self.node_vote_count = 0 # after process start ,the node has write vote to local
        self.node_start_time = datetime.datetime.today()
        self.round_recover_limit = 200

    def write_local_vote(self, vote):
        """Write the vote dict to leveldb.

        Args:
            vote(dict)

        Returns:

        """

        vote_id = vote['id']
        current_vote_timestamp = vote['vote']['timestamp']
        # previous_block = vote['vote']['previous_block']
        voting_for_block = vote['vote']['voting_for_block']
        node_pubkey = vote['node_pubkey']
        vote_key = voting_for_block + '-' + node_pubkey

        # if exists
        # if process wait long, the *.ldb files merge may cause the IO Errot,
        # try fix it by get the conn again
        try:
            exist_vote = ldb.get(self.conn_vote, vote_key) is not None
        except BaseException as msg:
            logging.warning(msg)
            self.conn_vote = ldb.LocalVote().conn['vote']
            exist_vote = ldb.get(self.conn_vote, vote_key) is not None

        exist_vote = ldb.get(self.conn_vote, vote_key) is not None
        if exist_vote:
            # logger.warning("\nThe vote[id={},vote_key={}] is already exist.\n".format(vote_id,vote_key))
            return None

        vote_json_str = rapidjson.dumps(vote)

        self.current_vote_num += 1

        ldb.insert(self.conn_vote, vote_key, vote_json_str, sync=False)

        vote_header_data_dict = dict()
        vote_header_data_dict['current_vote_id'] = vote_id
        vote_header_data_dict['current_vote_timestamp'] = current_vote_timestamp
        vote_header_data_dict['current_vote_num'] = self.current_vote_num
        ldb.batch_insertOrUpdate(self.conn_vote_header, vote_header_data_dict, transaction=True)
        del vote_header_data_dict

        self.node_vote_count += 1
        # logger.warning('The count of this node(since start[{}]) has write to local vote is: {}, current_vote_num is: {}'
        #     .format(self.node_start_time,self.node_vote_count, self.current_vote_num))

        info = "Vote[num={},voting_for_block={},id={}]"\
            .format(self.current_vote_num, vote['vote']['voting_for_block'], vote_id)
        logger.info(info)

        return None


def initial(current_vote_num, current_vote_timestamp):

    records_count = r.db(db_name).table('votes').count().run(get_conn())
    logger.info("initial local_vote records_count={}, current_vote_num={}".format(records_count, current_vote_num))
    records_count = records_count - current_vote_num
    if records_count >= 1:
        # here max is no effect!
        # return r.db('bigchain').table('votes').max(index='vote_timestamp').default(None).run(get_conn())
        return records_count, r.db(db_name).table('votes').max(index='vote_timestamp').run(get_conn())
    else:
        return None


def get_changefeed(current_vote_num, current_vote_timestamp):
    """Create and return the changefeed for the votes."""

    return ChangeFeed('votes', 'vote', ChangeFeed.INSERT | ChangeFeed.UPDATE, current_vote_timestamp,
                      round_recover_limit=200, round_recover_limit_max=2000, secondary_index='vote_timestamp',
                      prefeed=initial(current_vote_num, current_vote_timestamp))


def create_pipeline():
    """Create and return the pipeline of operations to be distributed
    on different processes."""

    conn_vote_header = ldb.LocalVote().conn['vote_header']
    conn_vote = ldb.LocalVote().conn['vote']

    current_vote_num = int(ldb.get_withdefault(conn_vote_header, 'current_vote_num', 0))
    current_vote_timestamp = ldb.get_withdefault(conn_vote_header, 'current_vote_timestamp','0')

    localvote_pipeline = LocalVote(current_vote_num=current_vote_num, conn_vote=conn_vote, conn_vote_header=conn_vote_header)

    pipeline = Pipeline([
        Node(localvote_pipeline.write_local_vote)
        # Node(localvote_pipeline.write_vote,fraction_of_cores=1)
        # Node(localvote_pipeline.write_vote,number_of_processes=1)
    ])

    return pipeline, current_vote_num, current_vote_timestamp


def start():
    """Create, start, and return the localvote pipeline."""

    pipeline, current_vote_num,current_vote_timestamp = create_pipeline()
    pipeline.setup(indata=get_changefeed(current_vote_num, current_vote_timestamp))
    pipeline.start()
    return pipeline
