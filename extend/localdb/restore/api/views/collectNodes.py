"""This module provides the blueprint for some basic API endpoints.

For more information please refer to the documentation on ReadTheDocs:
 - https://docs.bigchaindb.com/projects/server/en/latest/drivers-clients/http-client-server-api.html
"""
from flask import current_app, request, Blueprint, make_response
from flask_restful import Resource, Api
from extend.localdb.restore.api.views.base import make_error
from extend.localdb.restore.utils import leveldb_utils
from extend.localdb.restore.utils.common_utils import deal_response
from bigchaindb import config
node_collect = Blueprint('node_collect', __name__)
node_collect_api = Api(node_collect)

ldb = leveldb_utils.LocaldbUtils()

# Unfortunately I cannot find a reference to this decorator.
# This answer on SO is quite useful tho:
# - http://stackoverflow.com/a/13432373/597097


class NodeLocaldbCheck(Resource):

    def post(self):
        """API endpoint to push transactions to the Federation.

                Return:
                    A ``dict`` containing the data about the transaction.
                """
        # `force` will try to format the body of the POST request even if the `content-type` header is not
        # set to `application/json`

        req = request.get_json(force=True)
        if not req:
            return make_error(400, 'Invalid parameters')
        target = req['target']

        if target and target == 'check':
            can_access = ldb.check_conn_free(close_flag=False)
            response = {
                "free": True,
                "desc": 'can access the node localdb data.'
            }
            if not can_access:
                response['free'] = False
                response['desc'] = 'node localdb dirs is busy or not exist!'
            compress = config['restore_server']['compress']
            if compress:
                print("node check response {}".format(response))
            response = deal_response(response, make_response, compress=compress)
            return response
        else:
            return make_error(400, 'Invalid parameters')


class NodeBaseInfoApi(Resource):
    def post(self):
        """API endpoint to push transactions to the Federation.

        Return:
            A ``dict`` containing the data about the transaction.
        """
        # `force` will try to format the body of the POST request even if the `content-type` header is not
        # set to `application/json`

        req = request.get_json(force=True)
        if not req:
            return make_error(400, 'Invalid parameters')

        target = req['target']

        if target and target == 'node':
            compress = config['restore_server']['compress']
            response = ldb.get_restore_node_info()
            if compress:
                print("node info response {}".format(response))
            response = deal_response(response, make_response, compress=compress)
            return response
        else:
            return make_error(400, 'Invalid parameters')


class NodeBlockVotes(Resource):
    def post(self):
        """API endpoint to push transactions to the Federation.

                Return:
                    A ``dict`` containing the data about the transaction.
                """

        # `force` will try to format the body of the POST request even if the `content-type` header is not
        # set to `application/json`

        req = request.get_json(force=True)
        if not req:
            return make_error(400, 'Invalid parameters')

        current_block_num = req['current_block_num']
        if not isinstance(current_block_num,int):
            return make_error(400, 'Invalid parameters')

        response = ldb.get_restore_block_info(current_block_num)
        compress = config['restore_server']['compress']
        response = deal_response(response, make_response, compress=compress)
        if compress:
            print("block num={:<5} {}".format(current_block_num,response))
        return response

node_collect_api.add_resource(NodeLocaldbCheck,
                             '/check',
                             strict_slashes=False)
node_collect_api.add_resource(NodeBaseInfoApi,
                             '/node',
                             strict_slashes=False)
node_collect_api.add_resource(NodeBlockVotes,
                             '/block',
                             strict_slashes=False)
