
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
from bigchaindb.web.views.info import per_query

vote_views = Blueprint('vote_views', __name__)
vote_api = Api(vote_views)

class ApiPublickeySet(Resource):
    @per_query
    def post(self):
        pool = current_app.config['bigchain_pool']
        with pool() as b:
            try:
                pubkeyList = b.get_allPublicKey()
            except:
                return make_response(constant.RESPONSE_STATUS_SERVER_ERROR,
                                     constant.RESPONSE_CODE_SERVER_ERROR,
                                     "None")
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             pubkeyList)


##Router display
vote_api.add_resource(ApiPublickeySet,
                          '/publickeySet',
                          strict_slashes=False)
