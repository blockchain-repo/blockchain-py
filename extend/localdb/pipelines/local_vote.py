"""
This module  takes care of all the changes for bigchain and votes.
"""

from multipipes import Pipeline, Node
from extend.localdb.pipelines.local_utils import ChangeFeed

from extend.localdb.leveldb import utils as leveldb
import rapidjson
import datetime

import logging

logger = logging.getLogger(__name__)

class LocalVote(Node):
    """Monitor the vote changes and write to leveldb

    This class monitor the change for votes through changefeed
    and write the changes to localblock dir.

    Note:
        Methods of this class will be executed in different processes.
    """

    INSERT = 1
    DELETE = 2
    UPDATE = 4

    def __init__(self,current_vote_num=None,conn_votes=None,conn_header=None):
        """Initialize the LocalVotePipeline creator"""
        self.conn_header = conn_header or leveldb.LocalVote().conn['vote_header']
        self.conn_votes = conn_votes or leveldb.LocalVote().conn['votes']
        self.vote_num = current_vote_num or int(leveldb.get_withdefault(self.conn_header, 'vote_num', '0'))
        self.vote_count = 0 # after process start ,the node has write vote to local
        self.start_time = datetime.datetime.today()


    def write_vote(self,vote):
        """Write the vote dict to leveldb.

        Args:
            vote(dict)

        Returns:

        """

        vote_id = vote['id']
        current_vote_timestamp = vote['vote']['timestamp']
        previous_block = vote['vote']['previous_block']
        node_pubkey = vote['node_pubkey']
        vote_key = previous_block + '-' + node_pubkey

        # if exists
        exist_vote = leveldb.get(self.conn_votes,vote_key) is not None
        if exist_vote:
            logger.warning("\nThe vote[id={},vote_key={}] is already exist.\n".format(vote_id,vote_key))
            return None


        vote_json_str = rapidjson.dumps(vote)

        self.vote_num = self.vote_num + 1

        leveldb.insert(self.conn_votes, vote_key, vote_json_str, sync=False)

        vote_header_data_dict = dict()
        vote_header_data_dict['current_vote_id'] = vote_id
        vote_header_data_dict['current_vote_timestamp'] = current_vote_timestamp
        vote_header_data_dict['vote_num'] = self.vote_num
        leveldb.batch_insertOrUpdate(self.conn_header, vote_header_data_dict, transaction=True)
        del vote_header_data_dict

        # leveldb.update(self.conn_header, 'current_vote_id', vote_id, sync=False)
        # leveldb.update(self.conn_header, 'current_vote_timestamp', current_vote_timestamp, sync=False)
        # leveldb.update(self.conn_header, 'vote_num', self.vote_num, sync=False)

        self.vote_count = self.vote_count + 1
        logger.warning('The count of this node(since start[{}]) has write to local vote is: {}, vote_num is: {}'
            .format(self.start_time,self.vote_count, self.vote_num))

        info = "Current vote(has write into localdb) info \n[id={},vote_num={},vote_key(previous_block-node_pubkey)={}\n,voting_for_block={}]\n"\
            .format(vote_id,self.vote_num,vote_key, vote['vote']['voting_for_block'])
        logger.info(info)



        # self.get_local_votes_for_block(previous_block)

        return None


    def get_local_votes_for_block(self, block_id):
        """Only show the pre op result!"""

        votes = leveldb.get_prefix(self.conn_votes, block_id + '-')
        # previous_block_votes_info = "\nprevious_block votes info \n[id={},\nvotes={}]\n".format(block_id,votes)
        # logger.info(previous_block_votes_info)

        current_vote_timestamp = leveldb.get(self.conn_header, 'current_vote_timestamp')
        current_vote_id = leveldb.get(self.conn_header, 'current_vote_id')
        current_vote_num = leveldb.get(self.conn_header, 'vote_num')
        current_vote_inifo = "localdb info \n[vote_timestamp={},vote_num={},current_vote_id={}]\n"\
            .format(current_vote_timestamp,current_vote_num, current_vote_id)
        logger.info(current_vote_inifo)


def initial():
    # TODO maybe add the deal for pre localdb data check and recovery
    """Before the pipeline deal the changefeed, we can add the deal:
        1.get the Node missed or lost votes data between [minval,maxval] for bigchain;
        2.put the data into the special pipeline.

    Return lost votes
    """

    return None


def get_changefeed(current_vote_timestamp):
    """Create and return the changefeed for the votes."""
    logger.error('local_vote get_changefeed')
    return ChangeFeed('votes','vote',ChangeFeed.INSERT | ChangeFeed.UPDATE,current_vote_timestamp,
                      round_recover_limit=1000,round_recover_limit_max=1000,secondary_index='vote_timestamp',prefeed=initial())


def create_pipeline():
    """Create and return the pipeline of operations to be distributed
    on different processes."""

    conn_header = leveldb.LocalVote().conn['vote_header']
    conn_votes = leveldb.LocalVote().conn['votes']

    current_vote_num = int(leveldb.get_withdefault(conn_header, 'vote_num', 0))
    current_vote_timestamp = leveldb.get_withdefault(conn_header, 'current_vote_timestamp','0')

    localvote_pipeline = LocalVote(current_vote_num=current_vote_num,conn_votes=conn_votes,conn_header=conn_header)

    pipeline = Pipeline([
        Node(localvote_pipeline.write_vote)
        # Node(localvote_pipeline.write_vote,fraction_of_cores=1)
        # Node(localvote_pipeline.write_vote,number_of_processes=1)
    ])

    return pipeline,current_vote_timestamp


def start():
    """Create, start, and return the localvote pipeline."""

    pipeline,current_vote_timestamp = create_pipeline()
    pipeline.setup(indata=get_changefeed(current_vote_timestamp))
    pipeline.start()
    return pipeline