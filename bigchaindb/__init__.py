import copy
import os

# for multi apps, you should specify the app service name, setup_name and database.name
# and modify the port in server.bind, api_endpoint, restore_server.bind, restore_endpoint
# and make them unique and free

from bigchaindb.base_config import unichain_config

# from functools import reduce
# PORT_NUMBER = reduce(lambda x, y: x * y, map(ord, 'BigchainDB')) % 2**16
# basically, the port number is 9984
config = {
    'app': {
        'setup_name': '{}'.format(unichain_config['server_config']['setup_name']),  # BigchainDB
        'service_name': '{}'.format(unichain_config['server_config']['service_name']),  # unichain
    },
    'server': {
        # Note: this section supports all the Gunicorn settings:
        #       - http://docs.gunicorn.org/en/stable/settings.html
        'bind': os.environ.get('BIGCHAINDB_SERVER_BIND') or 'localhost:{}'.format(unichain_config['server_config']['server_port']),
        'workers': None,  # if none, the value will be cpu_count * 2 + 1
        'threads': None,  # if none, the value will be cpu_count * 2 + 1
    },
    'database': {
        'host': os.environ.get('BIGCHAINDB_DATABASE_HOST', 'localhost'),
        'port': 28015,
        'name': '{}'.format(unichain_config['server_config']['db_name']),
    },
    'keypair': {
        'public': None,
        'private': None,
    },
    'keyring': [],
    'statsd': {
        'host': 'localhost',
        'port': 8125,
        'rate': 0.01,
    },
    'need_local':False,
    'api_need_permission':False,
    'api_endpoint': os.environ.get('BIGCHAINDB_API_ENDPOINT') or 'http://localhost:{}/uniledger/v1'
        .format(unichain_config['server_config']['server_port']),
    'backlog_reassign_delay': 120,
    'logger_config' : {
        'debug_to_console' : False,
        'debug_to_file' : True
    },
    'argument_config' : {
        'use_local_keyrings':False,
        'query_all_txs':False,
        'split_backlog': False,
        'block_pipeline.block_size' : 2000,
        'block_pipeline.pipe_maxsize' : 5000,
        'block_pipeline.fraction_of_cores':1,
        'block_pipeline.get_txs_processes_num':30,
        'block_pipeline.get_txs_everytime':200,
        'block_pipeline.write.number_of_processes':3,
        'block_pipeline.timeout':1,
        'block_pipeline.block_timeout':15,
        'block_pipeline.block_size_detal':100,
        'election_pipeline.wait_time':10,
        'stale_pipeline.timeout':10,
        'stale_pipeline.assignee_timeout':100,
        'stale_pipeline.heartbeat_timeout':20,
        'vote_pipeline.fraction_of_cores':1,
        'vote_pipeline.validate_processes_num':30,
        'vote_pipeline.ungroup_processes_num':20
    },
    'order_api':'http://36.110.71.170:41',
    'restore_server': {
        'bind': os.environ.get('BIGCHAINDB_RESTORE_SERVER_BIND') or 'localhost:{}'
            .format(unichain_config['server_config']['restore_server_port']),
        'compress': True, # if compress, compress the response data
        'workers': None,  # if none, the value will be int(cpu_count/2) + 2
        'threads': None,  # if none, the value will be int(cpu_count/2) + 2
    },
    'restore_endpoint': os.environ.get('BIGCHAINDB_RESTORE_ENDPOINT') or
                        'http://localhost:{}/uniledger/v1/collect'.format(unichain_config['server_config']['restore_server_port']),
}


# We need to maintain a backup copy of the original config dict in case
# the user wants to reconfigure the node. Check ``bigchaindb.config_utils``
# for more info.
_config = copy.deepcopy(config)
from bigchaindb.core import Bigchain  # noqa
from bigchaindb.version import __version__  # noqa
