"""This module provides the blueprint for some basic API endpoints.

For more information please refer to the documentation on ReadTheDocs:
 - https://docs.bigchaindb.com/projects/server/en/latest/drivers-clients/http-client-server-api.html
"""

import flask
from flask import Blueprint
from flask import current_app
from flask import make_response
from flask import request
from flask_restful import reqparse

import bigchaindb
from bigchaindb import version
app_service_name = bigchaindb.config['app']['service_name']

info_views = Blueprint('info_views', __name__)

keys = ['8YQ6rPKrxuVpJ58DptJDevHX8L2S6zgkacL4hZk2zWVw','s9Z3jMPYX9tM1fxRpya9GVHMhg8ywMfoCfnxmgKD7JV',
        '3viQSvdWJc5AwAu8adKiMajfPDKPv2s7b55LcpVudKLn','FPZi8UULdLDvouhm9ysZV7pdFjEKARHarz4W9FGn2Gcx']

keys_url = ['acount','block-border-time-vote','transaction-condition','contract']

perminssion = ['per_acconut','per_query','per_trans','per_contract']


@info_views.route('/')
def home():
    return flask.jsonify({
        'software': '{}'.format(app_service_name),
        'version': version.__version__,
        'public_key': bigchaindb.config['keypair']['public'],
        'keyring': bigchaindb.config['keyring'],
        'api_endpoint': bigchaindb.config['api_endpoint']
    })


def per_acconut(func):
    def decorator(*args,**kwargs):
        need_per = bigchaindb.config['api_need_permission']
        print(need_per)
        if need_per:
            parser = reqparse.RequestParser()
            parser.add_argument('key')
            args = parser.parse_args()
            key = args['key']
            if key and key == '8YQ6rPKrxuVpJ58DptJDevHX8L2S6zgkacL4hZk2zWVw':
                return func(*args, **kwargs)
            else:
                return make_response(flask.jsonify({'error': 'Unauthorized access'}), 401)
                # return flask.redirect("/")
        else:
            return func(*args, **kwargs)
    return decorator

def per_query(func):
    def decorator(*args, **kwargs):
        need_per = bigchaindb.config['api_need_permission']
        if need_per:
            parser = reqparse.RequestParser()
            parser.add_argument('key')
            args = parser.parse_args()
            key = args['key']
            if key and key == 's9Z3jMPYX9tM1fxRpya9GVHMhg8ywMfoCfnxmgKD7JV':
                return func(*args, **kwargs)
            else:
                return make_response(flask.jsonify({'error': 'Unauthorized access'}), 401)
                # return flask.redirect("/")
        else:
            return func(*args, **kwargs)
    return decorator

def per_trans(func):
    def decorator(*args, **kwargs):
        need_per = bigchaindb.config['api_need_permission']
        if need_per:
            parser = reqparse.RequestParser()
            parser.add_argument('key')
            args = parser.parse_args()
            key = args['key']
            if key and key == '3viQSvdWJc5AwAu8adKiMajfPDKPv2s7b55LcpVudKLn':
                return func(*args, **kwargs)
            else:
                return make_response(flask.jsonify({'error': 'Unauthorized access'}), 401)
                # return flask.redirect("/")
        else:
            return func(*args, **kwargs)
    return decorator



def per_contract(func):
    def decorator(*args,**kwargs):
        need_per = bigchaindb.config['api_need_permission']
        if need_per:
            parser = reqparse.RequestParser()
            parser.add_argument('key')
            args = parser.parse_args()
            key = args['key']
            if key and key == 'FPZi8UULdLDvouhm9ysZV7pdFjEKARHarz4W9FGn2Gcx':
                return func(*args,**kwargs)
            else:
                return make_response(flask.jsonify({'error': 'Unauthorized access'}), 401)
                # return flask.redirect("/")
        else:
            return func(*args, **kwargs)
    return decorator
