"""This module provides the blueprint for some basic API endpoints.

For more information please refer to the documentation on ReadTheDocs:
 - https://docs.bigchaindb.com/projects/server/en/latest/drivers-clients/http-client-server-api.html
"""

import flask
from flask import Blueprint

import bigchaindb

info_views = Blueprint('restore_info_views', __name__)


@info_views.route('/')
def home():
    return flask.jsonify({
        'software': '{} restore'.format(bigchaindb.config['app']['service_name']),
        'public_key': bigchaindb.config['keypair']['public'],
        'keyring': bigchaindb.config['keyring'],
        'restore_endpoint': bigchaindb.config['restore_endpoint']
    })
