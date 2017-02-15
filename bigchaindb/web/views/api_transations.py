
"""
File:  api_timestat
Date:  2017-02-14
"""
import rapidjson
import uuid
import base
from flask import current_app, request, Blueprint
from flask_restful import Resource, Api

import bigchaindb
from bigchaindb.common.exceptions import InvalidHash, InvalidSignature
from bigchaindb.models import Transaction
from bigchaindb.web.views.base import make_error

transaction_views = Blueprint('transaction_views', __name__)
transaction_api = Api(transaction_views)

class ApiCreateByPayload(Resource):
    def post(self):
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             avgtime_json)
class ApiQueryByID(Resource):
    def post(self):
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             avgtime_json)

class ApiQueryTxsTotal(Resource):
    def post(self):
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             avgtime_json)

class ApiQueryTxsByRange(Resource):
    def post(self):
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             avgtime_json)

class ApiQueryGroupByBlock(Resource):
    def post(self):
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             avgtime_json)

##Router display
transaction_api.add_resource(ApiCreateByPayload,
                          '/createByPayload',
                          strict_slashes=False)
transaction_api.add_resource(ApiQueryByID,
                          '/queryByID',
                          strict_slashes=False)
transaction_api.add_resource(ApiQueryTxsTotal,
                          '/queryTxsTotal',
                          strict_slashes=False)
transaction_api.add_resource(ApiQueryTxsByRange,
                          '/queryTxsByRange',
                          strict_slashes=False)
transaction_api.add_resource(ApiQueryGroupByBlock,
                          '/queryGroupByBlock',
                          strict_slashes=False)
