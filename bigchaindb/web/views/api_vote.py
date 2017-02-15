
"""
File:  api_timestat
Date:  2017-02-14
"""
import rapidjson
import uuid
import base
from flask import current_app, request, Blueprint
from flask_restful import Resource, Api

import bigchaindb
from bigchaindb.common.exceptions import InvalidHash, InvalidSignature
from bigchaindb.models import Transaction
from bigchaindb.web.views.base import make_error

vote_views = Blueprint('vote_views', __name__)
vote_api = Api(vote_views)

class ApiPublickeySet(Resource):
    def post(self):
        pool = current_app.config['bigchain_pool']
        with pool() as unichain:
            avgtime,status = unichain.get_publickeySet()
        if not status:
            return make_response(constant.RESPONSE_STATUS_FAIL,
                                 constant.RESPONSE_CODE_FAIL,
                                 "response is none")
        avgtime_json = jsonify({'avgtime':avgtime})
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             avgtime_json)


##Router display
vote_api.add_resource(ApiPublickeySet,
                          '/publickeySet',
                          strict_slashes=False)
