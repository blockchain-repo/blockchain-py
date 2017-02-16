
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

transaction_views = Blueprint('transaction_views', __name__)
transaction_api = Api(transaction_views)

class ApiCreateByPayload(Resource):
    def post(self):
        # 单条payload创建交易
        # @common_api.route('/createTxByPayload/', methods=['POST'])
        # def createTxByPayload():
        pool = current_app.config['bigchain_pool']
        monitor = current_app.config['monitor']

        payload_dict = request.get_json(force=True)

        with pool() as b:
            tx = Transaction.create([b.me], [b.me], metadata=payload_dict)
            tx = tx.sign([b.me_private])
            rate = bigchaindb.config['statsd']['rate']
            with monitor.timer('write_transaction', rate=rate):
                b.write_transaction(tx)

        # tx = tx.to_dict()
        # return rapidjson.dumps(tx)
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             tx.to_dict())

class ApiQueryByID(Resource):
    def post(self):
    # 根据交易ID获取交易
    #@common_api.route('/getTxById/', methods=['POST'])
    #def getTxById():

        tx_id = request.get_json()["tx_id"]
        pool = current_app.config['bigchain_pool']
        with pool() as b:
            tx = b.get_transaction(tx_id)

        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             tx.to_dict())

class ApiQueryTxsTotal(Resource):
    def post(self):
    # 获取区块链中的总交易条数
    # @common_api.route('/getTxNumberInUnichain/', methods=['POST'])
    # def getTxNumberInUnichain():
        pool = current_app.config['bigchain_pool']
        with pool() as b:
            number = b.get_txNumber()
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             number)

class ApiQueryTxsByRange(Resource):
    def post(self):
    # 根据指定时间区间获取交易集
    # @common_api.route('/getTxsByTime/', methods=['POST'])
    # def getTxsByTime():
        startTime = request.get_json()['startTime']
        endTime = request.get_json()['endTime']
        pool = current_app.config['bigchain_pool']
        with pool() as b:
            txIdList = b.get_TxIdByTime(startTime, endTime)

        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             txIdList)

class ApiQueryGroupByBlock(Resource):
    def post(self):
    # 获取每区块中包含的交易条数
    # @common_api.route('/getTxNumOfAllBlock/', methods=['POST'])
    # def getTxNumOfAllBlock():
        pool = current_app.config['bigchain_pool']
        with pool() as b:
            blockIdTxList = b.get_txNumberOfAllBlock()

        blockIdTxList = list(blockIdTxList)
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             blockIdTxList)

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
