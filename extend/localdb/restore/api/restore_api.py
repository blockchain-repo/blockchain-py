"""Implementation of the `bigchaindb` command,
which is one of the commands in the BigchainDB
command-line interface.
"""

import sys
import logging
import argparse

import bigchaindb
import bigchaindb.config_utils
from bigchaindb.commands import utils
from extend.localdb.restore.utils.leveldb_utils import LocaldbUtils
from extend.localdb.restore.api import processes

app_service_name = bigchaindb.config['app']['service_name']
app_setup_name = bigchaindb.config['app']['setup_name']

logger = logging.getLogger(__file__)


def run_start(args):
    """ start api server"""

    ldb = LocaldbUtils()
    localdb_can_access = ldb.check_conn_free(close_flag=True)
    if not localdb_can_access:
        error_info = "You can`t start the {} restore, must shutdown the busy process or check other!"\
            .format(app_service_name)
        logger.error(error_info)
        exit(-1)

    bigchaindb.config_utils.autoconfigure(filename=args.config, force=True)
    logger.info('{} Version {}'.format(app_setup_name, bigchaindb.__version__))
    logger.info('start {} service...'.format(app_service_name))
    processes.start_restore()


def create_parser():
    parser = argparse.ArgumentParser(
        description='Collect Data from your node.',
        parents=[utils.base_parser])
    subparsers = parser.add_subparsers(title='Commands',
                                       dest='command')

    # parser for starting restore
    subparsers.add_parser('start',
                          help='Start {} API service'.format(app_setup_name))
    return parser


def main():
    utils.start(create_parser(), sys.argv[1:], globals())
