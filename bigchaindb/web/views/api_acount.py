from flask import current_app, request, Blueprint
from flask_restful import Resource, Api,reqparse
from bigchaindb.web.views import constant,parameters
from bigchaindb.web.views.base import make_response, check_request, make_error
from bigchaindb.web.views.info import per_acconut

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




acount_api.add_resource(ApiGetAccountInfos, '/apiGetAccountInfos', strict_slashes=False)
acount_api.add_resource(ApiUserAccountChangeRecord, '/apiUserAccountChangeRecord', strict_slashes=False)