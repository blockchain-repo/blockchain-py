from flask import current_app, request, Blueprint
from flask_restful import reqparse, Resource, Api

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
            outputs = bigchain.get_outputs_filtered(args['public_key'], include_spent)
            # NOTE: We pass '..' as a path to create a valid relative URI
            return outputs
            # return [u.to_uri('..') for u in outputs]


condition_api.add_resource(ApiGetUnspentTxs,
                          '/getUnspentTxs',
                          strict_slashes=False)