import rapidjson
import uuid
from flask import current_app, request, Blueprint
from flask_restful import Resource, Api, reqparse

import bigchaindb
from bigchaindb.common.exceptions import InvalidHash, InvalidSignature
from bigchaindb.models import Transaction
from bigchaindb.web.views.base import make_response, check_request, make_error
from bigchaindb.web.views import constant, parameters

from bigchaindb.common.exceptions import (
    AmountError,
    FulfillmentNotInValidBlock,
    DoubleSpend,
    InvalidHash,
    InvalidSignature,
    OperationError,
    TransactionDoesNotExist,
    TransactionOwnerError,
)
from bigchaindb.web.views.info import per_trans

common_views = Blueprint('common_views', __name__)
common_api = Api(common_views)

class ApiGetChainNodeCount(Resource):
    def get(self):
        pool = current_app.config['bigchain_pool']
        with pool() as b:
            chain_node_count = len(b.nodelist)
        print(chain_node_count)
        return chain_node_count

class ApiGetChainNodeKeyring(Resource):
    def get(self):
        pool = current_app.config['bigchain_pool']
        with pool() as b:
            chain_node_keyring = b.nodelist
        print(chain_node_keyring)
        return chain_node_keyring



common_api.add_resource(ApiGetChainNodeCount, '/getChainNodeCount', strict_slashes=False)

common_api.add_resource(ApiGetChainNodeKeyring, '/getChainNodeKeyring', strict_slashes=False)