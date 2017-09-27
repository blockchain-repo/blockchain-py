import logging
import multiprocessing as mp

import bigchaindb
from bigchaindb.pipelines import vote, block, election, stale, monitor
from bigchaindb.web import server

from extend.localdb.pipelines import local_block, local_vote
app_setup_name = bigchaindb.config['app']['setup_name']

logger = logging.getLogger(__name__)

BANNER = """
****************************************************************************
*                                                                          *
*   Initialization complete. Server is ready and waiting.                  *
*                                                                          *
*   Listening to client connections on: {:<20}               *
*                                                                          *
****************************************************************************
"""


def start():
    logger.info('Initializing {}...'.format(app_setup_name))
    logger.info('dianxin test =====================================')
    logger.info('dianxin test22222222222 =====================================')

    need_split_backlog = bigchaindb.config['argument_config']['split_backlog']
    if need_split_backlog:
        logger.info("NEED SIGNLE NODE BACKLOG T")
    else:
        logger.info("NEED SIGNLE NODE BACKLOG F")

    need_localdb = bigchaindb.config['need_local']
    if bigchaindb.config['api_need_permission']:
        logger.info("LOCAL LEVEL T")
    else:
        logger.info("LOCAL LEVEL F")

    # start the processes
    logger.info('Starting block')
    block.start()

    logger.info('Starting voter')
    vote.start()

    logger.info('Starting stale transaction monitor')
    #todo open it
    #stale.start()
    monitor.start()
    logger.info('Starting election')
    election.start()

    if need_localdb:
        # must start the localdb pipeline after origin pipeline
        # local_block pipeline store the cluster changefeed for table bigchain
        logger.info('Starting localblock')
        local_block.start()

        # local_block pipeline store the cluster changefeed for table votes
        logger.info('Starting localvoter')
        local_vote.start()

    # start message
    # logger.info(BANNER.format(bigchaindb.config['server']['bind']))

def start_api():
    # start the web api
    app_server = server.create_server(bigchaindb.config['server'])
    p_webapi = mp.Process(name='webapi', target=app_server.run)
    p_webapi.start()

    # start message
    if bigchaindb.config['api_need_permission']:
        logger.info("API PERMISSION LEVEL T")
    else:
        logger.info("API PERMISSION LEVEL F")

    logger.info(BANNER.format(bigchaindb.config['server']['bind']))
