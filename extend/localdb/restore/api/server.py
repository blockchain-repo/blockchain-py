"""This module contains basic functions to instantiate the BigchainDB API.

The application is implemented in Flask and runs using Gunicorn.
"""

import copy
import multiprocessing

from flask import Flask
import gunicorn.app.base

from extend.localdb.restore.api.views.info import info_views
from extend.localdb.restore.api.views.collectNodes import node_collect


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    """Run a **wsgi** app wrapping it in a Gunicorn Base Application.

    Adapted from:
     - http://docs.gunicorn.org/en/latest/custom.html
    """

    def __init__(self, app, options=None):
        """Initialize a new standalone application.

        Args:
            app: A wsgi Python application.
            options (dict): the configuration.

        """
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
        settings debug (bool): a flag to activate the debug mode for the app
            (default: False).
    """

    app = Flask(__name__)

    app.debug = settings.get('debug', False)

    app.register_blueprint(info_views, url_prefix='/collect')
    app.register_blueprint(node_collect, url_prefix='/uniledger/v1/collect')
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

    # use the localdb so, it must single process
    if not settings.get('workers'):
        settings['workers'] = (int(multiprocessing.cpu_count()/2) + 2)

    if not settings.get('threads'):
        settings['threads'] = (int(multiprocessing.cpu_count()/2) + 2)

    app = create_app(settings)
    standalone = StandaloneApplication(app, settings)
    return standalone
