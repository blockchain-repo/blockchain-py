"""
This module  takes care of all the changes for bigchain and votes.
"""

from multipipes import Pipeline, Node
from extend.localdb.pipelines.local_utils import ChangeFeed

from extend.localdb.leveldb import utils as leveldb
import rapidjson

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

    def __init__(self,conn_votes=None):
        """Initialize the LocalVotePipeline creator"""

        self.conn_votes = conn_votes or leveldb.LocalVote().conn['votes']
        self.vote_count = 0 # after process start ,the node has write vote to local
        # self.votes = []


    def write_vote(self,vote):
        """Write the vote dict to leveldb.

        Args:
            vote(dict)

        Returns:

        """

        previous_block = vote['vote']['previous_block']
        node_pubkey = vote['node_pubkey']
        vote_key = previous_block + '-' + node_pubkey
        vote_json_str = rapidjson.dumps(vote)

        leveldb.insert(self.conn_votes, vote_key, vote_json_str, sync=False)

        info = "current vote info \n[vote_key={}\n,previous_block={}\n,node_pubkey={}\n,voting_for_block={}]"\
            .format(vote_key,previous_block, node_pubkey, vote['vote']['voting_for_block'])
        logger.info(info)

        self.vote_count =self.vote_count + 1
        logger.warning('The count of this node(after start) has write to local vote is: {}'.format(self.vote_count))

        self.get_local_votes_for_block(previous_block)

        return None


    def get_local_votes_for_block(self, block_id):
        """Only show the pre op result!"""

        votes = leveldb.get_prefix(self.conn_votes, block_id + '-')
        previous_block_votes_info = "previous_block votes info \n[id={},\nvotes={}]\n".format(block_id,votes)
        logger.info(previous_block_votes_info)


def initial():
    # TODO maybe add the deal for pre localdb data check and recovery
    """Before the pipeline deal the changefeed, we can add the deal:
        1.get the Node missed or lost votes data between [minval,maxval] for bigchain;
        2.put the data into the special pipeline.

    Return lost votes
    """

    return None


def get_changefeed():
    """Create and return the changefeed for the votes."""

    return ChangeFeed('votes',ChangeFeed.INSERT | ChangeFeed.UPDATE,prefeed=initial())


def create_pipeline():
    """Create and return the pipeline of operations to be distributed
    on different processes."""

    conn_votes = leveldb.LocalVote().conn['votes']

    localvote_pipeline = LocalVote(conn_votes)

    pipeline = Pipeline([
        Node(localvote_pipeline.write_vote)
        # Node(localvote_pipeline.write_vote,fraction_of_cores=1)
        # Node(localvote_pipeline.write_vote,number_of_processes=1)
    ])

    return pipeline


def start():
    """Create, start, and return the localvote pipeline."""

    pipeline = create_pipeline()
    pipeline.setup(indata=get_changefeed())
    pipeline.start()
    return pipeline