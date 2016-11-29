"""
This module takes care of all the changes for bigchain and votes.
"""

from multipipes import Pipeline, Node
from extend.localdb.pipelines.local_utils import ChangeFeed

from bigchaindb.db.utils import get_conn
import bigchaindb
import rethinkdb as r
from extend.localdb.leveldb import utils as leveldb
import rapidjson

import logging

logger = logging.getLogger(__name__)


class LocalBlock(Node):
    """Monitor the block changes and write to leveldb.

    This class monitor the change for block through changefeed
    and write the changes to localblock dir.

    Note:
        Methods of this class will be executed in different processes.
    """

    INSERT = 1
    DELETE = 2
    UPDATE = 4

    def __init__(self,current_block_num=None,conn_header=None,conn_bigchain=None):
        """Initialize the LocalBlockPipeline creator."""

        self.conn_header = conn_header or leveldb.LocalBlock_Header().conn['block_header']
        self.conn_bigchain = conn_bigchain or leveldb.LocalBlock_Header().conn['bigchain']
        self.block_num = current_block_num or int(leveldb.get_withdefault(self.conn_header, 'block_num','0'))\
            if leveldb.get(self.conn_header, 'block_num') is not None else 1
        self.block_count = 0 # after process start ,the node has write block to local
        # self.blocks = []


    def write_block_header(self,block):
        """Write the block dict to leveldb.

        Instantly update the header dir, after change the block dir.

        Args:
           block(dict)

        Returns:

        """

        block_id = block['id']
        current_block_timestamp = block['block']['timestamp']
        block_size = len(block['block']['transactions'])
        block_json_str = rapidjson.dumps(block)

        self.block_num = self.block_num + 1

        leveldb.insert(self.conn_bigchain, block_id, block_json_str, sync=False)
        leveldb.update(self.conn_header, 'current_block_id', block_id, sync=False)
        leveldb.update(self.conn_header, 'current_block_timestamp', current_block_timestamp, sync=False)
        leveldb.update(self.conn_header, 'block_num', self.block_num, sync=False)

        info = "current block info \n[id={},block_num={},block_size={}]\n".format(block_id, self.block_num, block_size)
        logger.info(info)

        self.block_count =self.block_count + 1
        logger.warning('The count of this node(after start) has write to local block is: {}'.format(self.block_count))

        self.get_localblock_info()

        return None


    def get_localblock_info(self):
        """Only show the pre op result!"""

        current_block_timestamp = leveldb.get(self.conn_header, 'current_block_timestamp')
        current_block_id = leveldb.get(self.conn_header, 'current_block_id')
        current_block_num = leveldb.get(self.conn_header, 'block_num')
        current_block_inifo = "localdb info \n[current_block_timestamp={},block_num={},current__block_id={}]\n"\
            .format(current_block_timestamp,current_block_num, current_block_id)
        logger.info(current_block_inifo)


def init_localdb(current_block_num,conn_header,conn_bigchain):
    """Init leveldb dir [bigchain,header] when local_block pipeline run
    and update the Node info.

    Args:
        current_block_num(int): current_block counts
        conn_header: localdb header dir pointer
        conn_bigchain: localdb bigchian dir pointer
    Returns:

    """

    logger.info('leveldb init...')
    # logger.info('leveldb/header init host...' + str(bigchaindb.config['database']['host']))

    from urllib.parse import urlparse
    api_endpoint = urlparse(bigchaindb.config['api_endpoint'])
    node_host = api_endpoint.netloc.lstrip().split(':')[0]

    logger.info('leveldb/header init Node info: [host={},public_key={},private_key={}]'
                .format(node_host,bigchaindb.config['keypair']['public'],
                        bigchaindb.config['keypair']['private']))

    leveldb.update(conn_header, 'host', node_host)
    leveldb.update(conn_header, 'public_key', bigchaindb.config['keypair']['public'])
    leveldb.update(conn_header, 'private_key', bigchaindb.config['keypair']['private'])

    genesis_block_id = leveldb.get_withdefault(conn_header, 'genesis_block_id', '0')
    if current_block_num == 0:
        genesis_block = r.db('bigchain').table('bigchain').order_by(r.asc(r.row['block']['timestamp'])).limit(1).run(
            get_conn())[0]
        genesis_block_id = genesis_block['id']
        genesis_block_json_str = rapidjson.dumps(genesis_block)
        leveldb.insert(conn_bigchain, genesis_block_id, genesis_block_json_str)
        leveldb.insert(conn_header, 'genesis_block_id', genesis_block_id)
        leveldb.insert(conn_header, 'block_num', 1)
        leveldb.insert(conn_header, 'current_block_id', genesis_block_id)
        leveldb.insert(conn_header, 'current_block_timestamp', genesis_block['block']['timestamp'])
        logger.info("create the genesis block [id={}]".format(genesis_block_id))
        current_block_num = 1

    logger.info('leveldb/header genesis_block_id {}'.format(genesis_block_id))
    logger.info('leveldb init done')
    return current_block_num


def initial():
    # TODO maybe add the deal for pre localdb data check and recovery
    """Before the pipeline deal the changefeed, we can add the deal:
        1.get the Node missed or lost blocks data between [minval,maxval] for bigchain;
        2.put the data into the special pipeline.

    Return lost blocks
    """

    return None


def get_changefeed(current_block_timestamp):
    """Create and return the changefeed for the table bigchain."""

    return ChangeFeed('bigchain','block',ChangeFeed.INSERT | ChangeFeed.UPDATE,current_block_timestamp,
                      repeat_recover_round = 3,secondary_index='block_timestamp',prefeed=initial())


def create_pipeline():
    """Create and return the pipeline of operations to be distributed
    on different processes."""

    conn_header = leveldb.LocalBlock_Header().conn['block_header']
    conn_bigchain = leveldb.LocalBlock_Header().conn['bigchain']

    current_block_num = int(leveldb.get_withdefault(conn_header, 'block_num', 0))
    current_block_num = init_localdb(current_block_num,conn_header,conn_bigchain)

    current_block_timestamp = leveldb.get_withdefault(conn_header, 'current_block_timestamp','0')

    localblock_pipeline = LocalBlock(current_block_num=current_block_num,
                                     conn_header=conn_header,conn_bigchain=conn_bigchain)

    pipeline = Pipeline([
        Node(localblock_pipeline.write_block_header)
        # Node(localblock_pipeline.write_block_header,fraction_of_cores=1)
        # Node(localblock_pipeline.write_block_header,number_of_processes=1)
    ])

    return pipeline,current_block_timestamp


def start():
    """Create, start, and return the localblock pipeline."""

    pipeline,current_block_timestamp = create_pipeline()
    pipeline.setup(indata=get_changefeed(current_block_timestamp))
    pipeline.start()
    return pipeline