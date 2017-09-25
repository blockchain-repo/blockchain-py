from flask import current_app, request, Blueprint
from flask_restful import Resource, Api, reqparse
from bigchaindb.web.views import constant, parameters
from bigchaindb.web.views.base import make_response, check_request, make_error
from bigchaindb.web.views.info import per_acconut
from bigchaindb.common.crypto import generate_key_pair

acount_views = Blueprint('acount_views', __name__)
acount_api = Api(acount_views)


class ApiGetAccountInfos(Resource):
    @per_acconut
    def post(self):
        print("ApiGetAccountInfos")
        pool = current_app.config['bigchain_pool']
        param = request.get_json(force=True)
        print("1:", param)
        with pool() as bigchain:
            account_info = bigchain.getAccountInfo(param)

        print(account_info)

        return list(account_info)


class ApiUserAccountChangeRecord(Resource):
    @per_acconut
    def post(self):
        print("ApiUserAccountChangeRecord")
        pool = current_app.config['bigchain_pool']
        param = request.get_json(force=True)
        print("1:", param)
        with pool() as bigchain:
            account_record = bigchain.getAccountRecord(param)

        print(account_record)

        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             list(account_record))


class ApiGenerateKeyPairs(Resource):
    @per_acconut
    def get(self):
        pool = current_app.config['bigchain_pool']
        with pool() as bigchain:
            new_keypair = generate_key_pair()
            new_keypair_dict = {'private': new_keypair[0], 'public': new_keypair[1]}

        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "generate success",
                             new_keypair_dict)


acount_api.add_resource(ApiGetAccountInfos, '/apiGetAccountInfos', strict_slashes=False)
acount_api.add_resource(ApiUserAccountChangeRecord, '/apiUserAccountChangeRecord', strict_slashes=False)
acount_api.add_resource(ApiGenerateKeyPairs, '/apiGenerateKeyPairs', strict_slashes=False)
