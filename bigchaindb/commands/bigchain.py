"""Implementation of the `bigchaindb` command,
which is one of the commands in the BigchainDB
command-line interface.
"""

import logging
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
import bigchaindb.config_utils
import time
import random

from bigchaindb.models import Transaction
from bigchaindb.util import ProcessGroup
from bigchaindb import db
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
    bigchaindb.config_utils.autoconfigure( force=True)
    config = copy.deepcopy(bigchaindb.config)
    del config['CONFIGURED']
    private_key = config['keypair']['private']
    config['keypair']['private'] = 'x' * 45 if private_key else None
    print(json.dumps(config, indent=4, sort_keys=True))


def run_configure(args, skip_if_exists=False):
    """Run a script to configure the current node.

    Args:
        skip_if_exists (bool): skip the function if a config file already exists
    """

    # -------------------------------------------------------------
    server_config_path = args.config or bigchaindb.config_utils.CONFIG_SERVER_PATH
    server_config_file_exists = False
    # if the config path is `-` then it's stdout
    if server_config_path != '-':
        server_config_file_exists = os.path.exists(server_config_path)

    if server_config_file_exists and skip_if_exists:
        return

    if server_config_file_exists and not args.yes:
        want = input('Config file `{}` exists, do you want to override it? '
                     '(cannot be undone) [y/N]: '.format(server_config_path))
        if want != 'y':
            return

    server_conf = copy.deepcopy(bigchaindb.unichain_server_config)

    # Patch the default configuration with the new values
    server_conf = bigchaindb.config_utils.update(
            server_conf,
            bigchaindb.config_utils.env_config(bigchaindb.unichain_server_config))

    # print('Generating keypair', file=sys.stderr)
    # conf['keypair']['private'], conf['keypair']['public'] = crypto.generate_key_pair()

    if not args.yes:
        for key in ('bind', ):
            val = server_conf['server'][key]
            server_conf['server'][key] = \
                input('API Server {}? (default `{}`): '.format(key, val)) \
                or val

        for key in ('host', 'port', 'name'):
            val = server_conf['database'][key]
            server_conf['database'][key] = \
                input('Database {}? (default `{}`): '.format(key, val)) \
                or val

        for key in ('host', 'port', 'rate'):
            val = server_conf['statsd'][key]
            server_conf['statsd'][key] = \
                input('Statsd {}? (default `{}`): '.format(key, val)) \
                or val

        # val = conf['backlog_reassign_delay']
        # conf['backlog_reassign_delay'] = \
        #     input('Stale transaction reassignment delay (in seconds)? (default `{}`): '.format(val)) \
        #     or val

        # for key in ('debug_to_console', 'debug_to_file'):
        #     val = conf['logger_config'][key]
        #     conf['logger_config'][key] = \
        #         input('logger_config {}? (default `{}`): '.format(key, val)) \
        #         or val

        # for key in ('block_pipeline.block_size', 'block_pipeline.pipe_maxsize'):
        #     val = conf['argument_config'][key]
        #     conf['argument_config'][key] = \
        #         input('argument_config {}? (default `{}`): '.format(key, val)) \
        #         or val

        val = server_conf['restore_server']['bind']
        server_conf['restore_server']['bind'] = \
            input('Restore Server {}? (default `{}`): '.format('bind', val)) \
            or val

        val = server_conf['restore_server']['compress']
        compress = input('Restore Server {}? (default {}, only input False can be False): '.format('compress', val))
        if compress == 'False':
            compress = False
        elif val is None or compress.strip() == '':
            compress = val
        else:
            compress = True
            server_conf['restore_server']['compress'] = compress

    if server_config_path != '-':
        bigchaindb.config_utils.write_server_config(server_conf, server_config_path)
    else:
        print(json.dumps(server_conf, indent=4, sort_keys=True))
    print('server Configuration written to {}'.format(server_config_path), file=sys.stderr)
    print('Ready!', file=sys.stderr)




    # -------------------------------------------------------------

    key_config_path = args.config or bigchaindb.config_utils.CONFIG_KEY_PATH

    key_config_file_exists = False
    # if the config path is `-` then it's stdout
    if key_config_path != '-':
        key_config_file_exists = os.path.exists(key_config_path)

    if key_config_file_exists and skip_if_exists:
        return

    if key_config_file_exists and not args.yes:
        want = input('Config file `{}` exists, do you want to override it? '
                     '(cannot be undone) [y/N]: '.format(key_config_path))
        if want != 'y':
            return

    key_conf = copy.deepcopy(bigchaindb.unichain_key_config)

    # Patch the default configuration with the new values
    key_conf = bigchaindb.config_utils.update(
            key_conf,
        bigchaindb.config_utils.env_config(bigchaindb.unichain_key_config))

    print('Generating keypair', file=sys.stderr)
    key_conf['keypair']['private'], key_conf['keypair']['public'] = \
        crypto.generate_key_pair()
    if key_config_path != '-':
        if args.encrypt:
            bigchaindb.config_utils.write_config_encrypt(key_conf, key_config_path)
        else:
            bigchaindb.config_utils.write_key_config(key_conf, key_config_path)
    else:
        print(json.dumps(key_conf, indent=4, sort_keys=True))
    print('key Configuration written to {}'.format(key_config_path), file=sys.stderr)
    print('Ready!', file=sys.stderr)

    # -------------------------------------------------------------
    param_config_path = args.config or bigchaindb.config_utils.CONFIG_PARAM_PATH
    param_config_file_exists = False
    # if the config path is `-` then it's stdout
    if param_config_path != '-':
        param_config_file_exists = os.path.exists(param_config_path)

    if param_config_file_exists and skip_if_exists:
        return

    if param_config_file_exists and not args.yes:
        want = input('Config file `{}` exists, do you want to override it? '
                     '(cannot be undone) [y/N]: '.format(param_config_path))
        if want != 'y':
            return

    param_conf = copy.deepcopy(bigchaindb.unichain_param_config)

    # Patch the default configuration with the new values
    param_conf = bigchaindb.config_utils.update(
            param_conf,
        bigchaindb.config_utils.env_config(bigchaindb.unichain_param_config))

    # print('Generating keypair', file=sys.stderr)
    # conf['keypair']['private'], conf['keypair']['public'] = \
    #     crypto.generate_key_pair()

    if not args.yes:
        val = param_conf['backlog_reassign_delay']
        param_conf['backlog_reassign_delay'] = \
            input('Stale transaction reassignment delay (in seconds)? (default `{}`): '.format(val)) \
            or val

        for key in ('debug_to_console', 'debug_to_file'):
            val = param_conf['logger_config'][key]
            param_conf['logger_config'][key] = \
                input('logger_config {}? (default `{}`): '.format(key, val)) \
                or val

        for key in ('block_pipeline.block_size', 'block_pipeline.pipe_maxsize'):
            val = param_conf['argument_config'][key]
            param_conf['argument_config'][key] = \
                input('argument_config {}? (default `{}`): '.format(key, val)) \
                or val
    if param_config_path != '-':
        bigchaindb.config_utils.write_param_config(param_conf, param_config_path)
    else:
        print(json.dumps(param_conf, indent=4, sort_keys=True))
    print('param Configuration written to {}'.format(param_config_path), file=sys.stderr)
    print('Ready to go!', file=sys.stderr)


def run_export_my_pubkey(args):
    """Export this node's public key to standard output
    """
    # logger.debug('{} args = {}'.format(app_service_name, args))
    bigchaindb.config_utils.autoconfigure( force=True)
    pubkey = bigchaindb.config['keypair']['public']
    if pubkey is not None:
        print(pubkey)
    else:
        sys.exit("This node's public key wasn't set anywhere "
                 "so it can't be exported")
        # raises SystemExit exception
        # message is sent to stderr
        # exits with exit code 1 (signals tha an error happened)


def run_export_my_ip(args):
    """Export this node's api_endpoint ip to standard output
    """
    # logger.debug('{} args = {}'.format(app_service_name, args))
    bigchaindb.config_utils.autoconfigure( force=True)
    from urllib.parse import urlparse
    api_endpoint = urlparse(bigchaindb.config['api_endpoint'])
    node_ip = api_endpoint.netloc.lstrip().split(':')[0]
    if node_ip is not None:
        print(node_ip)
    else:
        sys.exit("This node's ip wasn't set anywhere "
                 "so it can't be exported")
        # raises SystemExit exception
        # message is sent to stderr
        # exits with exit code 1 (signals tha an error happened)


def run_init(args):
    """Initialize the database"""
    bigchaindb.config_utils.autoconfigure( force=True)
    # TODO Provide mechanism to:
    # 1. prompt the user to inquire whether they wish to drop the db
    # 2. force the init, (e.g., via -f flag)
    try:
        db.init()
    except DatabaseAlreadyExists:
        print('The database already exists.', file=sys.stderr)
        print('If you wish to re-initialize it, first drop it.', file=sys.stderr)


def run_drop(args):
    """Drop the database"""
    bigchaindb.config_utils.autoconfigure( force=True)
    db.drop(assume_yes=args.yes)


def run_start(args):
    """Start the processes to run the node"""
    logger.info('{} Version {}'.format(app_setup_name, bigchaindb.__version__))

    bigchaindb.config_utils.autoconfigure(force=True)

    if args.allow_temp_keypair:
        if not (bigchaindb.config['keypair']['private'] or
                bigchaindb.config['keypair']['public']):

            private_key, public_key = crypto.generate_key_pair()
            bigchaindb.config['keypair']['private'] = private_key
            bigchaindb.config['keypair']['public'] = public_key
        else:
            logger.warning('Keypair found, no need to create one on the fly.')

    if args.start_rethinkdb:
        try:
            proc = utils.start_rethinkdb()
        except StartupError as e:
            sys.exit('Error starting RethinkDB, reason is: {}'.format(e))
        logger.info('RethinkDB started with PID %s' % proc.pid)

    try:
        db.init()
    except DatabaseAlreadyExists:
        pass
    except KeypairNotFoundException:
        sys.exit("Can't start {}, no keypair found. "
                 'Did you run `{} configure`?'.format(app_setup_name, app_service_name))

    db.init_databaseData()

    logger.info('Starting {} main process with public key %s'.format(app_setup_name),
                bigchaindb.config['keypair']['public'])
    processes.start()

def _run_load(tx_left, stats):
    logstats.thread.start(stats)
    b = bigchaindb.Bigchain()

    while True:
        tx = Transaction.create([b.me], [([b.me],1)])
        tx = tx.sign([b.me_private])
        with monitor.timer('write_transaction', rate=0.01):
            b.write_transaction(tx)
            time.sleep(0.01*random.randint(1,100))
        stats['transactions'] += 1

        if tx_left is not None:
            tx_left -= 1
            if tx_left == 0:
                break
    # while True:
    #     relation = {'tets': 'relation'}!!!!!!
    #     contracts = {'tets': 'contracts'}
    #     tx = Transaction.create([b.me], [([b.me],1)],operation='CONTRACT',relation=relation,contracts=contracts,version=2)
    #     tx = tx.sign([b.me_private])
    #     with monitor.timer('write_transaction', rate=0.01):
    #         b.write_transaction(tx)
    #         time.sleep(0.01*random.randint(1,100))
    #     stats['transactions'] += 1
    #
    #     if tx_left is not None:
    #         tx_left -= 1
    #         if tx_left == 0:
    #             break

def run_load(args):
    bigchaindb.config_utils.autoconfigure( force=True)
    logger.info('Starting %s processes', args.multiprocess)
    stats = logstats.Logstats()
    logstats.thread.start(stats)

    tx_left = None
    if args.count > 0:
        tx_left = int(args.count / args.multiprocess)

    workers = ProcessGroup(concurrency=args.multiprocess,
                           target=_run_load,
                           args=(tx_left, stats.get_child()))
    workers.start()


def run_set_shards(args):
    for table in ['bigchain', 'backlog', 'votes','heartbeat', 'reassignnode', 'rewrite']:
        # See https://www.rethinkdb.com/api/python/config/
        table_config = r.table(table).config().run(db.get_conn())
        num_replicas = len(table_config['shards'][0]['replicas'])
        try:
            r.table(table).reconfigure(shards=args.num_shards, replicas=num_replicas).run(db.get_conn())
        except r.ReqlOpFailedError as e:
            logger.warn(e)


def run_set_replicas(args):
    for table in ['bigchain', 'backlog', 'votes','heartbeat', 'reassignnode', 'rewrite']:
        # See https://www.rethinkdb.com/api/python/config/
        table_config = r.table(table).config().run(db.get_conn())
        num_shards = len(table_config['shards'])
        try:
            r.table(table).reconfigure(shards=num_shards, replicas=args.num_replicas).run(db.get_conn())
        except r.ReqlOpFailedError as e:
            logger.warn(e)


def create_parser():
    parser = argparse.ArgumentParser(
        description='Control your {} node.'.format(app_setup_name),
        parents=[utils.base_parser])

    parser.add_argument('--dev-start-rethinkdb',
                        dest='start_rethinkdb',
                        action='store_true',
                        help='Run RethinkDB on start')

    parser.add_argument('--dev-allow-temp-keypair',
                        dest='allow_temp_keypair',
                        action='store_true',
                        help='Generate a random keypair on start')

    # all the commands are contained in the subparsers object,
    # the command selected by the user will be stored in `args.command`
    # that is used by the `main` function to select which other
    # function to call.
    subparsers = parser.add_subparsers(title='Commands',
                                       dest='command')

    # parser for writing a config file
    subparsers.add_parser('configure',
                          help='Prepare the config file '
                               'and create the node keypair')

    # parsers for showing/exporting config values
    subparsers.add_parser('show-config',
                          help='Show the current configuration')

    subparsers.add_parser('export-my-pubkey',
                          help="Export this node's public key")

    subparsers.add_parser('export-my-ip',
                          help="Export this node's ip for api_endpoint")

    # parser for database-level commands
    subparsers.add_parser('init',
                          help='Init the database')

    subparsers.add_parser('drop',
                          help='Drop the database')

    # parser for starting BigchainDB
    subparsers.add_parser('start',
                          help='Start {}'.format(app_setup_name))

    # parser for configuring the number of shards
    sharding_parser = subparsers.add_parser('set-shards',
                                            help='Configure number of shards')

    sharding_parser.add_argument('num_shards', metavar='num_shards',
                                 type=int, default=1,
                                 help='Number of shards')

    # parser for configuring the number of replicas
    replicas_parser = subparsers.add_parser('set-replicas',
                                            help='Configure number of replicas')

    replicas_parser.add_argument('num_replicas', metavar='num_replicas',
                                 type=int, default=1,
                                 help='Number of replicas (i.e. the replication factor)')

    load_parser = subparsers.add_parser('load',
                                        help='Write transactions to the backlog')

    load_parser.add_argument('-m', '--multiprocess',
                             nargs='?',
                             type=int,
                             default=False,
                             help='Spawn multiple processes to run the command, '
                                  'if no value is provided, the number of processes '
                                  'is equal to the number of cores of the host machine')

    load_parser.add_argument('-c', '--count',
                             default=0,
                             type=int,
                             help='Number of transactions to push. If the parameter -m '
                                  'is set, the count is distributed equally to all the '
                                  'processes')

    return parser


def main():
    utils.start(create_parser(), sys.argv[1:], globals())
