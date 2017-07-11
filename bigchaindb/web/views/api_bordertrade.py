from flask import current_app, request, Blueprint
from flask_restful import Resource, Api,reqparse
from bigchaindb.web.views import constant,parameters


bordertrade_views = Blueprint('bordertrade_views', __name__)
bordertrade_api = Api(bordertrade_views)


class Test(Resource):
    def post(self):
        print("test!---------------")


class ApiCustomsList(Resource):
    def post(self):
        print("ApiCustomsList")
        pool = current_app.config['bigchain_pool']
        # parser = reqparse.RequestParser()
        # parser.add_argument('type', required=True)
        # parser.add_argument('fuserName', required=True)
        # args = parser.parse_args()
        # print("1:",args)
        # type = request.get_json()['type']
        # fromuser = request.get_json()['fuserName']
        # print("1:",type,"--",fromuser)
        param = request.get_json(force=True)
        print("1:",param)
        with pool() as bigchain:
            customsList = bigchain.getCustomsList(param)
        return customsList

class ApiCustomsDetail(Resource):
    def post(self):
        print("ApiCustomsDetail")


class ApiTaxList(Resource):
    def post(self):
        print("ApiCustomsList")


class ApiTaxDetail(Resource):
    def post(self):
        print("ApiCustomsDetail")


class ApiOrderDetail(Resource):
    def post(self):
        print("ApiOrderDetail")



bordertrade_api.add_resource(Test, '/test', strict_slashes=False)
bordertrade_api.add_resource(ApiCustomsList, '/apiCustomsList', strict_slashes=False)
bordertrade_api.add_resource(ApiCustomsDetail, '/customsDetail', strict_slashes=False)
bordertrade_api.add_resource(ApiTaxList, '/taxList', strict_slashes=False)
bordertrade_api.add_resource(ApiTaxDetail, '/taxDetail', strict_slashes=False)
bordertrade_api.add_resource(ApiOrderDetail, '/orderDetail', strict_slashes=False)