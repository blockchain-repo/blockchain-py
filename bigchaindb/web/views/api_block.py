
"""
File:  api_timestat
Date:  2017-02-14
"""
import rapidjson
import uuid
from flask import current_app, request, Blueprint
from flask_restful import Resource, Api

import bigchaindb
from bigchaindb.common.exceptions import InvalidHash, InvalidSignature
from bigchaindb.models import Transaction
from bigchaindb.web.views.base import make_response,check_request
from bigchaindb.web.views import constant

block_views = Blueprint('block_views', __name__)
block_api = Api(block_views)


class ApiQueryByID(Resource):
    def post(self):
    # 根据区块ID获取区块
        if not check_request(request, "block_id"):
            return make_response(constant.RESPONSE_STATUS_FAIL,
                                 constant.RESPONSE_CODE_FAIL,
                                 "param block id not exist")
        block_id = request.get_json()["block_id"]
        pool = current_app.config['bigchain_pool']
        with pool() as b:
            try:
                block = b.get_block(block_id)
            except:
                return make_response(constant.RESPONSE_STATUS_ERROR,
                                     constant.RESPONSE_CODE_ERROR,
                                     "None")
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             block)

class ApiQueryTxsByID(Resource):
    def post(self):
    # 根据区块ID获取区块中的交易
        if not check_request(request, "block_id"):
            return make_response(constant.RESPONSE_STATUS_FAIL,
                                 constant.RESPONSE_CODE_FAIL,
                                 "param block id not exist")
        block_id = request.get_json()["block_id"]
        pool = current_app.config['bigchain_pool']
        with pool() as b:
            try:
                block = b.get_block(block_id)
            except:
                return make_response(constant.RESPONSE_STATUS_ERROR,
                                     constant.RESPONSE_CODE_ERROR,
                                     "None")
        print(block)
        txList = block["block"]['transactions']
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             txList)

class ApiQueryTxsCountByID(Resource):
    def post(self):
    # 根据区块ID获取区块中的交易条数
        if not check_request(request, "block_id"):
            return make_response(constant.RESPONSE_STATUS_FAIL,
                                 constant.RESPONSE_CODE_FAIL,
                                 "param block id not exist")
        block_id = request.get_json()["block_id"]
        pool = current_app.config['bigchain_pool']
        with pool() as b:
            try:
                number = b.get_txNumber(block_id)
            except:
                return make_response(constant.RESPONSE_STATUS_ERROR,
                                 constant.RESPONSE_CODE_ERROR,
                                 "None")
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             number)

class ApiQueryBlockCount(Resource):
    def post(self):
    # 获取区块链中的总区块数
        pool = current_app.config['bigchain_pool']
        with pool() as b:
            try:
                number = b.get_BlockNumber()
            except:
                return make_response(constant.RESPONSE_STATUS_ERROR,
                                 constant.RESPONSE_CODE_ERROR,
                                 "None")
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             number)

class ApiQueryBlocksByRange(Resource):
    def post(self):
    # 根据指定时间区间获取区块集
        if not check_request(request, "startTime"):
            return make_response(constant.RESPONSE_STATUS_FAIL,
                                 constant.RESPONSE_CODE_FAIL,
                                 "param startTime not exist")
        if not check_request(request, "endTime"):
            return make_response(constant.RESPONSE_STATUS_FAIL,
                                 constant.RESPONSE_CODE_FAIL,
                                 "param endtime not exist")

        startTime = request.json.get("startTime")
        endTime = request.json.get("endTime")

        pool = current_app.config['bigchain_pool']
        with pool() as b:
            try:
                blockIdList = b.get_BlockIdList(startTime, endTime)
            except:
                return make_response(constant.RESPONSE_STATUS_ERROR,
                                     constant.RESPONSE_CODE_ERROR,
                                     "None")
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             list(blockIdList))

class ApiQueryInvalidBlockTotal(Resource):
    def post(self):
    # 获取所有无效区块集
        pool = current_app.config['bigchain_pool']
        with pool() as b:
            try:
                invalidBlockIdList = b.get_invalidBlockIdList()
            except:
                return make_response(constant.RESPONSE_STATUS_ERROR,
                                     constant.RESPONSE_CODE_ERROR,
                                     "None")
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             invalidBlockIdList)

class ApiQueryInvalidBlockByRange(Resource):
    def post(self):
    # 获取指定时间区间内的无效区块集
        if not check_request(request, "startTime"):
            return make_response(constant.RESPONSE_STATUS_FAIL,
                                 constant.RESPONSE_CODE_FAIL,
                                 "param startTime not exist")
        if not check_request(request, "endTime"):
            return make_response(constant.RESPONSE_STATUS_FAIL,
                                 constant.RESPONSE_CODE_FAIL,
                                 "param endtime not exist")

        startTime = request.json.get("startTime")
        endTime = request.json.get("endTime")
        pool = current_app.config['bigchain_pool']
        with pool() as b:
            try:
                invalidBlockIdList = b.get_invalidBlockIdList(startTime, endTime)
            except:
                return make_response(constant.RESPONSE_STATUS_ERROR,
                                     constant.RESPONSE_CODE_ERROR,
                                     "None")
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             invalidBlockIdList)

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
