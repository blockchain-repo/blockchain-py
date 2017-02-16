
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
    # @common_api.route('/getBlockById/', methods=['POST'])
    # def getBlockById():
        print("in------")
        # block_id = request.args.get('block_id')
        print(request.get_json(force=True))

        block_id = ""
        pool = current_app.config['bigchain_pool']
        with pool() as b:
            try:
                block = b.get_block(block_id)
            except:
                return make_response(constant.RESPONSE_STATUS_ERROR,
                                     constant.RESPONSE_CODE_ERROR,
                                     "query success",
                                     block)
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             block)

class ApiQueryTxsByID(Resource):
    def post(self):
    # 根据区块ID获取区块中的交易
    # @common_api.route('/getAllTxsFromBlock/', methods=['POST'])
    # def getAllTxsFromBlock(block_id):
        block_id = request.args.get('block_id')
        pool = current_app.config['bigchain_pool']
        with pool() as b:
            try:
                block = b.get_block(block_id)
            except:
                return make_response(constant.RESPONSE_STATUS_ERROR,
                                     constant.RESPONSE_CODE_ERROR,
                                     "query success",
                                     "")
        txList = block['transactions']
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             txList.to_dict())

class ApiQueryTxsCountByID(Resource):
    def post(self):
    # 根据区块ID获取区块中的交易条数
    # @common_api.route('/getTxNumberInBlock/', methodget_publickeySets=['POST'])
    # def getTxNumberInBlock():
        block_id = request.args.get('block_id')
        pool = current_app.config['bigchain_pool']
        with pool() as b:
            number = b.get_txNumber(block_id)
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             number)

class ApiQueryBlockCount(Resource):
    def post(self):
    # 获取区块链中的总区块数
    # @common_api.route('/getBlockNumberInUnichain/', methods=['POST'])
    # def getBlockNumberInUnichain():
        pool = current_app.config['bigchain_pool']
        with pool() as b:
            number = b.get_BlockNumber()
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             number)

class ApiQueryBlocksByRange(Resource):
    def post(self):
    # 根据指定时间区间获取区块集
    # @common_api.route('/getBlocksByTime/', methods=['POST'])
    # def getBlocksByTime():
        startTime = request.args.get('startTime')
        endtime = request.args.get('endtime')
        pool = current_app.config['bigchain_pool']
        with pool() as b:
            blockIdList = b.get_BlockIdList(startTime=startTime, endtime=endtime)
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             blockIdList)

class ApiQueryInvalidBlockTotal(Resource):
    def post(self):
    # 获取所有无效区块集
    # @common_api.route('/getInvalidBlcok/', methods=['POST'])
    # def getInvalidBlcok():
        pool = current_app.config['bigchain_pool']
        with pool() as b:
            invalidBlockIdList = b.get_invalidBlockIdList()
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             invalidBlockIdList)

class ApiQueryInvalidBlockByRange(Resource):
    def post(self):
    # 获取指定时间区间内的无效区块集
    # @common_api.route('/getInvalidBlcokByTime/', methods=['POST'])
    # def getInvalidBlcokByTime():
        startTime = request.args.get('startTime')
        endtime = request.args.get('endtime')
        pool = current_app.config['bigchain_pool']
        with pool() as b:
            invalidBlockIdList = b.get_invalidBlockIdList(startTime, endtime)
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
