from flask import current_app, request, Blueprint
from flask_restful import reqparse, Resource, Api
from bigchaindb.web.views.base import make_response,check_request,make_error
from bigchaindb.web.views import constant,parameters

from bigchaindb.web.views import parameters

condition_views = Blueprint('condition_views', __name__)
condition_api = Api(condition_views)

class ApiGetUnspentTxs(Resource):
    def get(self):
        """API endpoint to retrieve a list of links to transaction
        outputs.

            Returns:
                A :obj:`list` of :cls:`str` of links to outputs.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('public_key', type=parameters.valid_ed25519, required=True)
        parser.add_argument('unspent', type=parameters.valid_bool)
        args = parser.parse_args()

        pool = current_app.config['bigchain_pool']
        include_spent = not args['unspent']

        with pool() as bigchain:
            outputs = bigchain.get_outputs_filtered_not_include_freeze(args['public_key'], include_spent)
            # NOTE: We pass '..' as a path to create a valid relative URI
            return make_response(constant.RESPONSE_STATUS_SUCCESS,
                            constant.RESPONSE_CODE_SUCCESS,
                            "sucess",
                            outputs)
            # return [u.to_uri('..') for u in outputs]


class ApiGetFreezeUnspentTx(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('public_key', type=parameters.valid_ed25519, required=True)
        parser.add_argument('unspent', type=parameters.valid_bool)
        parser.add_argument('contract_id')
        parser.add_argument('task_id')
        args = parser.parse_args()

        include_spent = not args['unspent']
        contract_id = args['contract_id']
        task_id = args['task_id']
        pub_key = args['public_key']

        pool = current_app.config['bigchain_pool']
        with pool() as bigchain:
            outputs = bigchain.get_freeze_output(pub_key,contract_id,task_id,include_spent)
            return make_response(constant.RESPONSE_STATUS_SUCCESS,
                            constant.RESPONSE_CODE_SUCCESS,
                            "sucess",
                            outputs)



condition_api.add_resource(ApiGetUnspentTxs,
                          '/getUnspentTxs',
                          strict_slashes=False)
condition_api.add_resource(ApiGetFreezeUnspentTx,'/getFreezeUnspentTx',strict_slashes=False)