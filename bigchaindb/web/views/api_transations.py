
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
from bigchaindb.web.views.base import make_response,check_request,make_error
from bigchaindb.web.views import constant

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

        if not tx:
            tx_result = {}
            result_messages = "tx not exist!"
        else:
            tx_result = tx.to_dict()
            result_messages = "query success"

        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             result_messages,
                             tx_result)

class ApiQueryByID(Resource):
    def post(self):
    # 根据交易ID获取交易
    #@common_api.route('/getTxById/', methods=['POST'])
    #def getTxById():
        type = request.get_json()["type"]

        if not check_request(request, "type"):
            return make_response(constant.RESPONSE_STATUS_FAIL,
                                 constant.RESPONSE_CODE_FAIL,
                                 "param type not exist")
        tx_id = request.get_json()["tx_id"]
        if not check_request(request, "tx_id"):
            return make_response(constant.RESPONSE_STATUS_FAIL,
                             constant.RESPONSE_CODE_FAIL,
                             "param tx_id not exist")

        pool = current_app.config['bigchain_pool']
        with pool() as b:
            if type == '1':
                tx = list(b.get_tx_by_id(tx_id))
            elif type == '2':
                tx = b.get_blocks_status_containing_tx(tx_id)
            elif type == '3':
                tx = b.get_transaction(tx_id)
                tx = tx.to_dict()

        if not tx:
            tx = {}
            result_messages = "tx not exist!"
        else:
            # tx_result = tx.to_dict()
            result_messages = "query success"

        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             result_messages,
                             tx)

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
        startTime = request.get_json()['beginTime']
        if not check_request(request, "beginTime"):
            return make_response(constant.RESPONSE_STATUS_FAIL,
                             constant.RESPONSE_CODE_FAIL,
                             "param beginTime not exist")

        endTime = request.get_json()['endTime']
        if not check_request(request, "endTime"):
            return make_response(constant.RESPONSE_STATUS_FAIL,
                                 constant.RESPONSE_CODE_FAIL,
                                 "param endTime not exist")

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
                             blockIdTxList)\



class ApiCreateByUser(Resource):
    def post(self):
        pool = current_app.config['bigchain_pool']
        monitor = current_app.config['monitor']

        payload_dict = request.get_json(force=True)

        with pool() as b:
            tx = Transaction.create(['6GSFmL4kcK6YJVFC2xq1KegmezhMRNhXLGmRAkLEt9Zq'], ['6GSFmL4kcK6YJVFC2xq1KegmezhMRNhXLGmRAkLEt9Zq'], metadata=payload_dict)
            tx = tx.sign(['5y5whz73ixHsoRi27U9eBqPykk5pzv1Y1nUrCf3SBQWV'])
            rate = bigchaindb.config['statsd']['rate']
            with monitor.timer('write_transaction', rate=rate):
                b.write_transaction(tx)

        # tx = tx.to_dict()
        # return rapidjson.dumps(tx)

        if not tx:
            tx_result = {}
            result_messages = "tx not exist!"
        else:
            tx_result = tx.to_dict()
            result_messages = "query success"

        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             result_messages,
                             tx_result)


class ApiCreateOrTransferTx(Resource):
    def post(self):
        pool = current_app.config['bigchain_pool']
        tx = request.get_json(force=True)
        tx_obj = Transaction.from_dict(tx)
        with pool() as bigchain:
            try:
                bigchain.validate_transaction(tx_obj)
            except (ValueError,
                    OperationError,
                    TransactionDoesNotExist,
                    TransactionOwnerError,
                    FulfillmentNotInValidBlock,
                    DoubleSpend,
                    InvalidHash,
                    InvalidSignature,
                    AmountError) as e:
                return make_error(
                    400,
                    'Invalid transaction ({}): {}'.format(type(e).__name__, e)
                )
            else:
                bigchain.write_transaction(tx_obj)

        return tx, 202



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



transaction_api.add_resource(ApiCreateByUser,
                          '/createByUser',
                          strict_slashes=False)

# CREATE|TRANSFER tx api for client
transaction_api.add_resource(ApiCreateOrTransferTx,
                          '/createOrTransferTx',
                          strict_slashes=False)

