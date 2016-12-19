"""Implementation of the `bigchaindb` command,
which is one of the commands in the BigchainDB
command-line interface.
"""

import os
import sys
import argparse
import copy
import json
import builtins

import logstats

from bigchaindb.common import crypto
from bigchaindb.common.exceptions import (StartupError,
                                          DatabaseAlreadyExists,
                                          KeypairNotFoundException)
import rethinkdb as r

import bigchaindb
import bigchaindb.config_utils
from bigchaindb.models import Transaction
from bigchaindb.util import ProcessGroup
from bigchaindb import db
from bigchaindb.commands import utils
from bigchaindb import processes

from bigchaindb.monitor import Monitor
monitor = Monitor()

import time
import random
from bigchaindb.logger_api import *
#import logging
logger = logging.getLogger("unichain_api")
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
    logger.info('BigchainDB Version {}'.format(bigchaindb.__version__))
    logger.info('start api service....')
    processes.start_api()

def create_parser():
    parser = argparse.ArgumentParser(
        description='Control your BigchainDB node.',
        parents=[utils.base_parser])
    subparsers = parser.add_subparsers(title='Commands',
                                       dest='command')
    # parser for starting BigchainDB
    subparsers.add_parser('start',
                          help='Start Unichain API service')
    return parser

def main():
    utils.start(create_parser(), sys.argv[1:], globals())
