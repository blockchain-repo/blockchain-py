"""
This module takes care of all the changes for bigchain and votes.
"""

from multipipes import Pipeline, Node
from extend.localdb.pipelines.local_utils import ChangeFeed

from bigchaindb.db.utils import get_conn
import bigchaindb
import rethinkdb as r
from extend.localdb.leveldb import utils as ldb
import rapidjson
import datetime

import logging

logger = logging.getLogger(__name__)


class LocalBlock():
    """Monitor the block changes and write to leveldb.

    This class monitor the change for block through changefeed
    and write the changes to localblock dir.

    Note:
        Methods of this class will be executed in different processes.
    """

    INSERT = 1
    DELETE = 2
    UPDATE = 4

    def __init__(self, current_block_num=None, conn_block=None, conn_block_header=None, conn_block_records=None,
                 total_block_txs_num=None):
        """Initialize the LocalBlockPipeline creator."""
        self.conn_block = conn_block or ldb.LocalBlock().conn['block']
        self.conn_block_header = conn_block_header or ldb.LocalBlock().conn['block_header']
        self.conn_block_records = conn_block_records or ldb.LocalBlock().conn['block_records']
        self.current_block_num = current_block_num or int(ldb.get_withdefault(self.conn_block_header
                                                                              , 'current_block_num', '0'))
        self.total_block_txs_num = total_block_txs_num or int(ldb.get_withdefault(self.conn_block_header
                                                                              , 'total_block_txs_num', '0'))
        self.node_block_count = 0 # after process start ,the node has write block to local
        self.node_start_time = datetime.datetime.today()

    def write_local_block(self, block):
        """Write the block dict to leveldb.

        Instantly update the header dir, after change the block dir.

        Args:
           block(dict)

        Returns:

        """

        block_id = block['id']

        # if exists
        # also can search the block_records dir
        # if process wait long, the *.ldb files merge may cause the IO Errot,
        # try fix it by get the conn again
        try:
            exist_block = ldb.get(self.conn_block, block_id) is not None
        except BaseException as msg:
            logging.warning(msg)
            self.conn_block = ldb.LocalBlock().conn['block']
            exist_block = ldb.get(self.conn_block, block_id) is not None

        if exist_block:
            # logger.warning("\nThe block[id={}] is already exist.\n".format(block_id))
            return None

        current_block_timestamp = block['block']['timestamp']
        block_txs_num = len(block['block']['transactions'])
        block_json_str = rapidjson.dumps(block)

        self.current_block_num += 1
        self.total_block_txs_num += block_txs_num

        ldb.insert(self.conn_block, block_id, block_json_str, sync=False)

        # write the block_records [block_num=block_id-block_txs-accumulate_block_txs] for restore pos
        # before the block_header write, can ensure the data precise
        block_records_val = "{}-{}-{}".format(block_id, block_txs_num, self.total_block_txs_num)
        ldb.insert(self.conn_block_records, self.current_block_num, block_records_val)

        block_header_data_dict = dict()
        block_header_data_dict['current_block_id'] = block_id
        block_header_data_dict['current_block_timestamp'] = current_block_timestamp
        block_header_data_dict['current_block_num'] = self.current_block_num
        block_header_data_dict['total_block_txs_num'] = self.total_block_txs_num
        ldb.batch_insertOrUpdate(self.conn_block_header,block_header_data_dict,transaction=True)
        del block_header_data_dict

        self.node_block_count += 1
        # logger.warning('The count of this node(since start[{}]) has write to local block is: {}, current_block_num is: {}'
        #                .format(self.node_start_time,self.node_block_count,self.current_block_num))

        info = "Block[num={},size={},id={},accumulate_txs={}]".format(
            self.current_block_num, block_txs_num, block_id, self.total_block_txs_num)
        logger.info(info)

        return None


def init_localdb(current_block_num, conn_block, conn_block_header, conn_block_records):
    """Init leveldb dir [bigchain,header] when local_block pipeline run
    and update the Node info.

    Args:
        current_block_num(int): current_block counts
        conn_block: localdb block dir pointer
        conn_block_header: localdb block_header dir pointer
        conn_block_records: localdb block_records dir pointer
    Returns:

    """

    logger.info('localdb init...')
    # logger.info('leveldb/header init host...' + str(bigchaindb.config['database']['host']))

    from urllib.parse import urlparse
    api_endpoint = urlparse(bigchaindb.config['api_endpoint'])
    node_host = api_endpoint.netloc.lstrip().split(':')[0]
    node_pubkey = bigchaindb.config['keypair']['public']
    node_prikey = bigchaindb.config['keypair']['private']
    node_prikey_encode = len(node_prikey) * '*'
    logger.info('localdb/node_info init Node info: [host={},public_key={},private_key={}]'
                .format(node_host,node_pubkey,node_prikey_encode))

    # insert or update this node info and close the conn after write
    conn_node_info = ldb.LocalBlock().conn['node_info']
    node_restart_times = int(ldb.get_withdefault(conn_node_info, 'restart_times', '0'))
    node_restart_times += 1
    node_info_data_dict = dict()
    node_info_data_dict['host'] = node_host
    node_info_data_dict['public_key'] = node_pubkey
    node_info_data_dict['private_key'] = node_prikey
    node_info_data_dict['restart_times'] = node_restart_times
    ldb.batch_insertOrUpdate(conn_node_info, node_info_data_dict, transaction=True)
    ldb.close(conn_node_info)
    del node_info_data_dict

    # genesis block write
    genesis_block_id = ldb.get_withdefault(conn_block_header, 'genesis_block_id', '0')
    if current_block_num == 0:
        genesis_block = r.db('bigchain').table('bigchain').order_by(r.asc(r.row['block']['timestamp'])).limit(1).run(
            get_conn())[0]
        current_block_txs_num = len(genesis_block['block']['transactions'])
        genesis_block_id = genesis_block['id']
        genesis_block_json_str = rapidjson.dumps(genesis_block)
        ldb.insert(conn_block, genesis_block_id, genesis_block_json_str)
        current_block_num = 1

        block_header_data_dict = dict()
        block_header_data_dict['genesis_block_id'] = genesis_block_id
        block_header_data_dict['current_block_id'] = genesis_block_id
        block_header_data_dict['current_block_timestamp'] = genesis_block['block']['timestamp']
        block_header_data_dict['current_block_num'] = current_block_num
        block_header_data_dict['total_block_txs_num'] = current_block_txs_num
        ldb.batch_insertOrUpdate(conn_block_header, block_header_data_dict, transaction=True)
        del block_header_data_dict

        logger.info("localdb write the genesis block [id={}]".format(genesis_block_id))

        # write the block_records [block_num=block_id-block_txs-total_block-txs]
        block_records_val = "{}-{}-{}".format(genesis_block_id, current_block_txs_num, current_block_txs_num)
        ldb.insert(conn_block_records, current_block_num, block_records_val)

    logger.info('localdb genesis_block_id {}'.format(genesis_block_id))
    logger.info('localdb init done')

    return current_block_num


def initial(current_block_num, current_block_timestamp):

    records_count = r.db('bigchain').table('bigchain').count().run(get_conn())
    records_count = records_count - current_block_num
    return records_count, r.db('bigchain').table('bigchain').max(index='block_timestamp').default(None).run(get_conn())

def get_changefeed(current_block_num, current_block_timestamp):
    """Create and return the changefeed for the table bigchain."""

    return ChangeFeed('bigchain','block', ChangeFeed.INSERT | ChangeFeed.UPDATE, current_block_timestamp,
                      round_recover_limit=200, round_recover_limit_max=2000, secondary_index='block_timestamp',
                      prefeed=initial(current_block_num, current_block_timestamp))


def create_pipeline():
    """Create and return the pipeline of operations to be distributed
    on different processes."""

    conn_block = ldb.LocalBlock().conn['block']
    conn_block_header = ldb.LocalBlock().conn['block_header']
    conn_block_records = ldb.LocalBlock().conn['block_records']

    current_block_num = int(ldb.get_withdefault(conn_block_header, 'current_block_num', 0))
    current_block_num = init_localdb(current_block_num, conn_block, conn_block_header, conn_block_records)

    current_block_timestamp = ldb.get_withdefault(conn_block_header, 'current_block_timestamp','0')
    total_block_txs_num = int(ldb.get_withdefault(conn_block_header
                                                       , 'total_block_txs_num', '0'))
    localblock_pipeline = LocalBlock(current_block_num=current_block_num, conn_block=conn_block,
                                     conn_block_header=conn_block_header, conn_block_records=conn_block_records,
                                     total_block_txs_num=total_block_txs_num)

    pipeline = Pipeline([
        Node(localblock_pipeline.write_local_block)
        # Node(localblock_pipeline.write_block_header,fraction_of_cores=1)
        # Node(localblock_pipeline.write_block_header,number_of_processes=1)
    ])

    return pipeline, current_block_num, current_block_timestamp


def start():
    """Create, start, and return the localblock pipeline."""

    pipeline, current_block_num, current_block_timestamp = create_pipeline()
    pipeline.setup(indata=get_changefeed(current_block_num, current_block_timestamp))
    pipeline.start()
    return pipeline
