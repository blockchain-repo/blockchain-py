
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

block_views = Blueprint('block_views', __name__)
block_api = Api(block_views)


class ApiQueryByID(Resource):
    def post(self):
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             avgtime_json)

class ApiQueryTxsByID(Resource):
    def post(self):
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             avgtime_json)

class ApiQueryTxsCountByID(Resource):
    def post(self):
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             avgtime_json)

class ApiQueryBlockCount(Resource):
    def post(self):
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             avgtime_json)

class ApiQueryBlocksByRange(Resource):
    def post(self):
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             avgtime_json)

class ApiQueryInvalidBlockTotal(Resource):
    def post(self):
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             avgtime_json)

class ApiQueryInvalidBlockByRange(Resource):
    def post(self):
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             avgtime_json)

##Router display
block_api.add_resource(ApiQueryByID,
                          '/queryByID',
                          strict_slashes=False)
block_api.add_resource(ApiQueryTxsByID,
                          '/queryTxsByID',
                          strict_slashes=False)
block_api.add_resource(ApiQueryTxsCountByID,
                          '/queryTxsCountByID',
                          strict_slashes=False)
block_api.add_resource(ApiQueryBlockCount,
                          '/queryBlockCount',
                          strict_slashes=False)
block_api.add_resource(ApiQueryBlocksByRange,
                          '/queryBlocksByRange',
                          strict_slashes=False)
block_api.add_resource(ApiQueryInvalidBlockTotal,
                          '/queryInvalidBlockTotal',
                          strict_slashes=False)
block_api.add_resource(ApiQueryInvalidBlockByRange,
                          '/queryInvalidBlockByRange',
                          strict_slashes=False)
