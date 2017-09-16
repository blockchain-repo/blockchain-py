"""This module contains basic functions to instantiate the BigchainDB API.

The application is implemented in Flask and runs using Gunicorn.
"""

import copy
import multiprocessing

from flask import Flask
import gunicorn.app.base

from bigchaindb import util
from bigchaindb import Bigchain
from bigchaindb.web.views.info import info_views
from bigchaindb.web.views.api_transations import transaction_views
from bigchaindb.web.views.api_block import block_views
from bigchaindb.web.views.api_vote import vote_views
from bigchaindb.web.views.api_timestat import timestat_views
from bigchaindb.web.views.api_condition import condition_views
from bigchaindb.web.views.api_contract import contract_views
from bigchaindb.web.views.api_bordertrade import bordertrade_views
from bigchaindb.web.views.api_acount import acount_views
# from bigchaindb.web.apiForVeracity.apiForVeracity import testVeracity_api
from bigchaindb.monitor import Monitor


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    """Run a **wsgi** app wrapping it in a Gunicorn Base Application.

    Adapted from:
     - http://docs.gunicorn.org/en/latest/custom.html
    """

    def __init__(self, app, options=None):
        '''Initialize a new standalone application.

        Args:
            app: A wsgi Python application.
            options (dict): the configuration.

        '''
        self.options = options or {}
        self.application = app
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = dict((key, value) for key, value in self.options.items()
                      if key in self.cfg.settings and value is not None)

        for key, value in config.items():
            # not sure if we need the `key.lower` here, will just keep
            # keep it for now.
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def create_app(settings):
    """Return an instance of the Flask application.

    Args:
        debug (bool): a flag to activate the debug mode for the app
            (default: False).
    """

    app = Flask(__name__)

    app.debug = settings.get('debug', False)

    app.config['bigchain_pool'] = util.pool(Bigchain, size=settings.get('threads', 4))
    app.config['monitor'] = Monitor()
    #welcome view
    app.register_blueprint(info_views, url_prefix='/')
    #transaction operate view
    app.register_blueprint(transaction_views, url_prefix='/uniledger/v1/transaction')
    #block operate view
    app.register_blueprint(block_views, url_prefix='/uniledger/v1/block')
    #vote operate view
    app.register_blueprint(vote_views, url_prefix='/uniledger/v1/vote')
    #timestat operate view
    app.register_blueprint(timestat_views, url_prefix='/uniledger/v1/timestat')

    app.register_blueprint(condition_views, url_prefix='/uniledger/v1/condition')

    app.register_blueprint(contract_views, url_prefix='/uniledger/v1/contract')

    app.register_blueprint(bordertrade_views, url_prefix='/uniledger/v1/bordertrade')

    app.register_blueprint(acount_views, url_prefix='/uniledger/v1/account')
    return app


def create_server(settings):
    """Wrap and return an application ready to be run.

    Args:
        settings (dict): a dictionary containing the settings, more info
            here http://docs.gunicorn.org/en/latest/settings.html

    Return:
        an initialized instance of the application.
    """

    settings = copy.deepcopy(settings)

    if not settings.get('workers'):
        settings['workers'] = (multiprocessing.cpu_count() * 2) + 1

    if not settings.get('threads'):
        settings['threads'] = (multiprocessing.cpu_count() * 2) + 1

    app = create_app(settings)
    standalone = StandaloneApplication(app, settings)
    return standalone
