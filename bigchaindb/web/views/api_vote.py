
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

vote_views = Blueprint('vote_views', __name__)
vote_api = Api(vote_views)

class ApiPublickeySet(Resource):
    def post(self):
    # @common_api.route('/getAllPublicKey/', methods=['POST'])
    # def getAllPublicKey():
        pool = current_app.config['bigchain_pool']
        with pool() as b:
            pubkeyList = b.get_allPublicKey()
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             pubkeyList)


##Router display
vote_api.add_resource(ApiPublickeySet,
                          '/publickeySet',
                          strict_slashes=False)
