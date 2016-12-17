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
logger = logging.getLogger(__file__)


def run_start(args):
    """ start api server"""

    ldb = LocaldbUtils()
    localdb_can_access = ldb.check_conn_free(close_flag=False)
    if not localdb_can_access:
        error_info = "You can`t start the restore, must shutdown the busy process or check other!"
        logger.error(error_info)
        exit(-1)

    bigchaindb.config_utils.autoconfigure(filename=args.config, force=True)
    logger.info('BigchainDB Version {}'.format(bigchaindb.__version__))
    logger.info('start restore service...')
    processes.start_restore()


def create_parser():
    parser = argparse.ArgumentParser(
        description='Collect Data from your node.',
        parents=[utils.base_parser])
    subparsers = parser.add_subparsers(title='Commands',
                                       dest='command')

    # parser for starting restore
    subparsers.add_parser('start',
                          help='Start restore API service')
    return parser


def main():
    utils.start(create_parser(), sys.argv[1:], globals())
