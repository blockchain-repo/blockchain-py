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


class ApiGetChainNodeDetail(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('node_pubkeys', type=str, required=False)
        args = parser.parse_args()

        node_pubkeys = args['node_pubkeys']
        if node_pubkeys is None:
            node_pubkey_list = None
        else:
            node_pubkey_list = node_pubkeys.split(",")
            node_pubkey_list = list(set(node_pubkey_list))
            node_pubkey_list = [x for x in node_pubkey_list if x.strip() != '']
        print("ApiGetChainNodeDetail params: {}".format(node_pubkey_list))

        pool = current_app.config['bigchain_pool']
        with pool() as b:
            chain_detail = b.get_block_chain_node_detail(node_pubkey_list)
            try:
                chain_detail = b.get_block_chain_node_detail(node_pubkey_list)
            except Exception as ex:
                print(ex)
                return make_response(constant.RESPONSE_STATUS_SERVER_ERROR,
                                     constant.RESPONSE_CODE_SERVER_ERROR,
                                     "None")
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "ApiGetChainNodeDetail query success",
                             chain_detail)


common_api.add_resource(ApiGetChainNodeCount, '/getChainNodeCount', strict_slashes=False)

common_api.add_resource(ApiGetChainNodeKeyring, '/getChainNodeKeyring', strict_slashes=False)

common_api.add_resource(ApiGetChainNodeDetail, '/getChainNodeDetail', strict_slashes=False)