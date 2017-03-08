"""Implementation of the `bigchaindb` command,
which is one of the commands in the BigchainDB
command-line interface.
"""

import logging
import sys
import argparse
import copy
import json
import builtins

import bigchaindb.config_utils
from bigchaindb.commands import utils
from bigchaindb import processes
from bigchaindb import logger

from bigchaindb.monitor import Monitor
monitor = Monitor()

app_service_name = bigchaindb.config['app']['service_name']
app_setup_name = bigchaindb.config['app']['setup_name']

logger = logging.getLogger(__name__)

# We need this because `input` always prints on stdout, while it should print
# to stderr. It's a very old bug, check it out here:
# - https://bugs.python.org/issue1927


def input(prompt):
    print(prompt, end='', file=sys.stderr)
    return builtins.input()


def run_show_config(args):
    """Show the current configuration"""
    # TODO Proposal: remove the "hidden" configuration. Only show config. If
    # the system needs to be configured, then display information on how to
    # configure the system.
    bigchaindb.config_utils.autoconfigure(filename=args.config, force=True)
    config = copy.deepcopy(bigchaindb.config)
    del config['CONFIGURED']
    private_key = config['keypair']['private']
    config['keypair']['private'] = 'x' * 45 if private_key else None
    print(json.dumps(config, indent=4, sort_keys=True))

def run_start(args):
    """ start api server"""
    logger.info('{} Version {}'.format(app_setup_name, bigchaindb.__version__))
    logger.info('start api service....')
    processes.start_api()

def create_parser():
    parser = argparse.ArgumentParser(
        description='Control your {} node.'.format(app_setup_name),
        parents=[utils.base_parser])
    subparsers = parser.add_subparsers(title='Commands',
                                       dest='command')
    # parser for starting BigchainDB
    subparsers.add_parser('start',
                          help='Start {} API service'.format(app_setup_name))
    return parser

def main():
    utils.start(create_parser(), sys.argv[1:], globals())
