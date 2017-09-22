from flask import current_app, request, Blueprint
from flask_restful import Resource, Api,reqparse
from bigchaindb.web.views import constant,parameters
from bigchaindb.web.views.info import per_query

bordertrade_views = Blueprint('bordertrade_views', __name__)
bordertrade_api = Api(bordertrade_views)


class Test(Resource):
    @per_query
    def post(self):
        print("test!---------------")


class ApiCustomsList(Resource):
    @per_query
    def post(self):
        print("ApiCustomsList")
        pool = current_app.config['bigchain_pool']
        param = request.get_json(force=True)
        print("1:",param)
        with pool() as bigchain:
            customsList = bigchain.getCustomsList(param)
        # print(customsList)
        return customsList

class ApiCustomsDetail(Resource):
    @per_query
    def post(self):
        print("ApiCustomsDetail")
        pool = current_app.config['bigchain_pool']
        param = request.get_json(force=True)
        print("1:", param)
        customsDetail = None
        with pool() as bigchain:
            customsDetails = bigchain.getCustomsDeatil(param)

            if customsDetails:
                for c in customsDetails:
                    customsDetail = c
        # print(customsDetail)
        return customsDetail


class ApiTaxList(Resource):
    @per_query
    def post(self):
        print("ApiTaxList")
        pool = current_app.config['bigchain_pool']
        param = request.get_json(force=True)
        print("1:",param)
        with pool() as bigchain:
            # if param['itemTitle'] == '':
            #
            #     taxList = bigchain.getTaxList(param)
            #     passstrict_
            # else:
            #     taxList = bigchain.getTaxList(param)
            taxList = bigchain.getTaxList(param)
        print(taxList)


        return taxList

class ApiTaxDetail(Resource):
    @per_query
    def post(self):
        print("ApiTaxDetail")
        pool = current_app.config['bigchain_pool']
        param = request.get_json(force=True)
        print("1:", param)
        with pool() as bigchain:
            taxDetail = None
            taxDetails,goodsTitle = bigchain.getTaxDeatil(param)
            if taxDetails:
                for c in taxDetails:
                    taxDetail = c
                    taxDetail['goodsTitle'] = goodsTitle
        # print(taxDetail)
        return taxDetail

# apiGetOrderCodeByTitle
class ApiGetOrderCodeByTitle(Resource):
    @per_query
    def post(self):
        print("ApiGetOrderCodeByTitle")
        pool = current_app.config['bigchain_pool']
        param = request.get_json(force=True)
        print("1:", param)
        with pool() as bigchain:
            taxDetails = bigchain.getOrderCodeByTitle(param)
        print(taxDetails)
        return taxDetails


class ApiGetGoosTitle(Resource):
    @per_query
    def post(self):
        print("ApiGetGoosTitle")
        pool = current_app.config['bigchain_pool']
        param = request.get_json(force=True)
        print("1:", param)
        with pool() as bigchain:
            title = bigchain.getGoosTitleByCode(param)
        print(title)
        return title

bordertrade_api.add_resource(Test, '/test', strict_slashes=False)
bordertrade_api.add_resource(ApiCustomsList, '/apiCustomsList', strict_slashes=False)
bordertrade_api.add_resource(ApiCustomsDetail, '/customsDetail', strict_slashes=False)
bordertrade_api.add_resource(ApiTaxList, '/taxList', strict_slashes=False)
bordertrade_api.add_resource(ApiTaxDetail, '/taxDetail', strict_slashes=False)
bordertrade_api.add_resource(ApiGetOrderCodeByTitle, '/apiGetOrderCodeByTitle', strict_slashes=False)
bordertrade_api.add_resource(ApiGetGoosTitle, '/apiGetGoosTitle', strict_slashes=False)

