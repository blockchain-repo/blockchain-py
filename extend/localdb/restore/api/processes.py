import logging
import multiprocessing as mp

from extend.localdb.restore.api import server
from bigchaindb import config
app_service_name = config['app']['service_name']
app_setup_name = config['app']['setup_name']

logger = logging.getLogger(__file__)

BANNER = """
****************************************************************************
*                                                                          *
*   Initialization complete. {} Restore Server is ready and waiting.
*   You can send HTTP requests via the HTTP API documented in the
*   {} Restore Server docs at:
*    https://xxx.com/http-api
*
*   Listening to client connections on: {:<15}
*                                                                          *
****************************************************************************
"""


def start_restore():
    logger.info('Starting {} Restore Process...'.format(app_setup_name))

    app_server = server.create_server(config['restore_server'])
    p_web_api = mp.Process(name='{}_restore_api'.format(app_service_name), target=app_server.run)
    p_web_api.start()

    # start message
    logger.info(BANNER.format(app_setup_name, app_setup_name, config['restore_endpoint']))

