from flask import current_app, request, Blueprint
from flask_restful import Resource, Api

from bigchaindb.models import Transaction
from bigchaindb.web.views.base import make_response, check_request
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
from bigchaindb.web.views.info import per_contract

contract_views = Blueprint('contract_views', __name__)
contract_api = Api(contract_views)


# class ApiCreateContract(Resource):
#     def post(self):
#         print("createContract")
#         pool = current_app.config['bigchain_pool']
#
#         contract = request.get_json(force=True)
#         contract_obj = Transaction.from_dict(contract)
#
#         # TODO validate data structure /version=2;opercation=Contract;has relation and contact
#
#         with pool() as bigchain:
#             try:
#                 bigchain.validate_transaction(contract_obj)
#             except (ValueError,
#                     OperationError,
#                     TransactionDoesNotExist,
#                     TransactionOwnerError,
#                     FulfillmentNotInValidBlock,
#                     DoubleSpend,
#                     InvalidHash,
#                     InvalidSignature,
#                     AmountError) as e:
#                 return make_response(constant.RESPONSE_STATUS_PARAM_ERROE,
#                                  constant.RESPONSE_CODE_PARAM_ERROE,
#                                  "invalidate contract.")
#             else:
#                 tx_result = bigchain.write_transaction(contract_obj)
#                 result_messages = "add contract success"
#
#         return make_response(constant.RESPONSE_STATUS_SUCCESS,
#                              constant.RESPONSE_CODE_SUCCESS,
#                              result_messages,
#                              tx_result)


class ApiCreateContractTx(Resource):
    @per_contract
    def post(self):
        print("createContractTx")

        pool = current_app.config['bigchain_pool']
        contractTx = request.get_json(force=True)
        # print(111)
        print(contractTx)

        contractTx_obj = Transaction.from_dict(contractTx)
        # TODO validate data structure /version=2;opercation=create/transfer;    has relation and contact?
        print("222====",contractTx_obj)
        with pool() as bigchain:
            try:
                # print("333")
                bigchain.validate_transaction(contractTx_obj)
                # print("444")
            except (ValueError,
                    OperationError,
                    TransactionDoesNotExist,
                    TransactionOwnerError,
                    FulfillmentNotInValidBlock,
                    DoubleSpend,
                    InvalidHash,
                    InvalidSignature,
                    AmountError) as e:
                return make_response(constant.RESPONSE_STATUS_PARAM_ERROE,
                                     constant.RESPONSE_CODE_PARAM_ERROE,
                                     "invalidate contract transaction.")
            # print(contractTx_obj.metadata.to_dict())
            tx_result = bigchain.write_transaction(contractTx_obj)
            result_messages = "add contract transaction success"

        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             result_messages,
                             tx_result)


class ApiGetContract(Resource):
    @per_contract
    def post(self):
        print("getContract")

        contract_id = request.get_json()["contract_id"]
        if not check_request(request, "contract_id"):
            return make_response(constant.RESPONSE_STATUS_PARAM_ERROE,
                             constant.RESPONSE_CODE_PARAM_ERROE,
                             "param contract_id not exist")
        pool = current_app.config['bigchain_pool']
        with pool() as bigchain:
            contract = bigchain.get_contract_by_id(contract_id)
        if not contract:
            contract = {}
            return make_response(constant.RESPONSE_STATUS_SUCCESS_NODATA,
                                 constant.RESPONSE_CODE_SUCCESS_NODATA,
                                 "contract not exist!",
                                 list(contract))
        else:
            res = list(contract)
            # print("getContract return", res)
            return make_response(constant.RESPONSE_STATUS_SUCCESS,
                                 constant.RESPONSE_CODE_SUCCESS,
                                 "query success",
                                 res)


class ApiGetContractTx(Resource):
    @per_contract
    def post(self):
        print("getContractTx")

        tx_id = request.get_json()["tx_id"]
        if not check_request(request, "tx_id"):
            return make_response(constant.RESPONSE_STATUS_PARAM_ERROE,
                                 constant.RESPONSE_CODE_PARAM_ERROE,
                                 "param tx_id not exist")
        pool = current_app.config['bigchain_pool']
        with pool() as bigchain:
            txs = bigchain.get_contract_txs_by_tx_id(tx_id)

        if not txs:
            txs = {}
            return make_response(constant.RESPONSE_STATUS_SUCCESS_NODATA,
                                 constant.RESPONSE_CODE_SUCCESS_NODATA,
                                 "contract or tx not exist!",
                                 list(txs))
        else:
            return make_response(constant.RESPONSE_STATUS_SUCCESS,
                                 constant.RESPONSE_CODE_SUCCESS,
                                 "query success",
                                 list(txs))


class ApiGetContractRecord(Resource):
    @per_contract
    def post(self):
        print("getContractRecord")

        contract_id = request.get_json()["contract_id"]
        if not check_request(request, "contract_id"):
            return make_response(constant.RESPONSE_STATUS_PARAM_ERROE,
                                 constant.RESPONSE_CODE_PARAM_ERROE,
                                 "param contract_id not exist")

        pool = current_app.config['bigchain_pool']
        with pool() as bigchain:
            txs = bigchain.get_contract_record_by_contract_id(contract_id)

        if not txs:
            txs = {}
            return make_response(constant.RESPONSE_STATUS_SUCCESS_NODATA,
                                 constant.RESPONSE_CODE_SUCCESS_NODATA,
                                 "contract or tx not exist!",
                                 txs)
        else:
            return make_response(constant.RESPONSE_STATUS_SUCCESS,
                                 constant.RESPONSE_CODE_SUCCESS,
                                 "query success",
                                 txs)


# class ApiFreezeAsset(Resource):
#     def post(self):
#         print("freezeAsset")
#         pool = current_app.config['bigchain_pool']
#         freezeTx = request.get_json(force=True)
#         freezeTx_obj = Transaction.from_dict(freezeTx)
#
#         # TODO validate data structure /version=2;opercation=freezeasset;    has relation and contact?
#
#         with pool() as bigchain:
#             try:
#                 bigchain.validate_transaction(freezeTx_obj)
#             except (ValueError,
#                     OperationError,
#                     TransactionDoesNotExist,
#                     TransactionOwnerError,
#                     FulfillmentNotInValidBlock,
#                     DoubleSpend,
#                     InvalidHash,
#                     InvalidSignature,
#                     AmountError) as e:
#                 return make_response(constant.RESPONSE_STATUS_PARAM_ERROE,
#                                      constant.RESPONSE_CODE_PARAM_ERROE,
#                                      "invalidate freeze asset transaction.")
#             tx_result = bigchain.write_transaction(freezeTx_obj)
#             result_messages = "freeze asset success"
#
#         return make_response(constant.RESPONSE_STATUS_SUCCESS,
#                              constant.RESPONSE_CODE_SUCCESS,
#                              result_messages,
#                              tx_result)


# class ApiUnfreeezeAsset(Resource):
#     def post(self):
#         print("unfreezeAsset")
#         pool = current_app.config['bigchain_pool']
#         freezeTx = request.get_json(force=True)
#         freezeTx_obj = Transaction.from_dict(freezeTx)
#
#         # TODO validate data structure /version=2;opercation=unfreezrasset;    has relation and contact?
#
#         with pool() as bigchain:
#             try:
#                 bigchain.validate_transaction(freezeTx_obj)
#             except (ValueError,
#                     OperationError,
#                     TransactionDoesNotExist,
#                     TransactionOwnerError,
#                     FulfillmentNotInValidBlock,
#                     DoubleSpend,
#                     InvalidHash,
#                     InvalidSignature,
#                     AmountError) as e:
#                 return make_response(constant.RESPONSE_STATUS_PARAM_ERROE,
#                                      constant.RESPONSE_CODE_PARAM_ERROE,
#                                      "invalidate freeze asset transaction.")
#             tx_result = bigchain.write_transaction(freezeTx_obj)
#             result_messages = "freeze asset success"
#
#         return make_response(constant.RESPONSE_STATUS_SUCCESS,
#                              constant.RESPONSE_CODE_SUCCESS,
#                              result_messages,
#                              tx_result)


# class ApiFrozenAsset(Resource):
#     def post(self):
#         print("frozenAsset")
#         public_key = request.get_json()["public_key"]
#         if not check_request(request, "public_key"):
#             return make_response(constant.RESPONSE_STATUS_PARAM_ERROE,
#                                  constant.RESPONSE_CODE_PARAM_ERROE,
#                                  "param public_key not exist")
#         unspent = request.get_json()["unspent"]
#         if not check_request(request, "unspent"):
#             return make_response(constant.RESPONSE_STATUS_PARAM_ERROE,
#                                  constant.RESPONSE_CODE_PARAM_ERROE,
#                                  "param unspent not exist")
#
#         pool = current_app.config['bigchain_pool']
#         # the asset frozen by contract
#         with pool() as bigchain:
#             try:
#                 result = bigchain.get_freeze_output(public_key,unspent=unspent)
#             except(Exception):
#                 return make_response(constant.RESPONSE_STATUS_SERVER_ERROE,
#                                      constant.RESPONSE_CODE_SERVER_ERROR,
#                                      "get frozen asset failed.")
#             if not result:
#                 result = {}
#                 return make_response(constant.RESPONSE_STATUS_SUCCESS_NODATA,
#                                      constant.RESPONSE_CODE_SUCCESS_NODATA,
#                                      "no asset exist!",
#                                      result)
#             else:
#                 return make_response(constant.RESPONSE_STATUS_SUCCESS,
#                                      constant.RESPONSE_CODE_SUCCESS,
#                                      "query success",
#                                      result)

class ApiGetTxByConHashId(Resource):
    @per_contract
    def post(self):
        print("ApiGetTxByConHashId")
        contract_hash_id = request.get_json()["contract_hash_id"]
        if not check_request(request, "contract_hash_id"):
            return make_response(constant.RESPONSE_STATUS_PARAM_ERROE,
                                 constant.RESPONSE_CODE_PARAM_ERROE,
                                 "param contract_hash_id not exist")
        pool = current_app.config['bigchain_pool']
        with pool() as bigchain:
            try:
                result = bigchain.get_tx_by_contract_hash_id(contract_hash_id)
                # print(result)
            except(Exception):
                return make_response(constant.RESPONSE_STATUS_SERVER_ERROE,
                                     constant.RESPONSE_CODE_SERVER_ERROR,
                                     "get output failed.")
            if not result:
                result = {}
                return make_response(constant.RESPONSE_STATUS_SUCCESS_NODATA,
                                     constant.RESPONSE_CODE_SUCCESS_NODATA,
                                     "no asset exist!",
                                     result)
            else:
                return make_response(constant.RESPONSE_STATUS_SUCCESS,
                                     constant.RESPONSE_CODE_SUCCESS,
                                     "query success",
                                     list(result))

# class ApiGetCanSpend(Resource):
#     def post(self):
#         print("getCanSpend")
#         # all asset include the asset frozen by the contract
#
#         return
#
#
# class ApiGetUnSpend(Resource):
#     def post(self):
#         print("getUnSpend")
#         # the asset which does not contains the asset frozen by the contract
#
#
#         return


# contract_api.add_resource(ApiCreateContract, '/createContract', strict_slashes=False)
contract_api.add_resource(ApiCreateContractTx, '/createContractTx', strict_slashes=False)
contract_api.add_resource(ApiGetContract, '/getContract', strict_slashes=False)
contract_api.add_resource(ApiGetContractTx, '/getContractTx', strict_slashes=False)
contract_api.add_resource(ApiGetTxByConHashId,'/getTxByConHashId', strict_slashes=False)
contract_api.add_resource(ApiGetContractRecord, '/getContractRecord', strict_slashes=False)
# contract_api.add_resource(ApiFreezeAsset, '/freezeAsset', strict_slashes=False)
# contract_api.add_resource(ApiUnfreeezeAsset, '/unfreezeAsset', strict_slashes=False)
# contract_api.add_resource(ApiFrozenAsset, '/frozenAsset', strict_slashes=False)
# contract_api.add_resource(ApiGetCanSpend, '/getCanSpend', strict_slashes=False)
# contract_api.add_resource(ApiGetUnSpend, '/getUnSpend', strict_slashes=False)
