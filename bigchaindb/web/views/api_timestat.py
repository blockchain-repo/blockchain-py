"""
File:  api_timestat
Date:  2017-02-14
"""
import rapidjson
import uuid
from flask import current_app, request, Blueprint, jsonify
from flask_restful import Resource, Api

import bigchaindb
from bigchaindb.common.exceptions import InvalidHash, InvalidSignature
from bigchaindb.models import Transaction
from bigchaindb.web.views.base import make_response,check_request
from bigchaindb.web.views import constant

timestat_views = Blueprint('timestat_views', __name__)
timestat_api = Api(timestat_views)


class ApiTxCreateAvgTimeByRange(Resource):
    def post(self):
        print("txCreateAvgTime")
        if not check_request(request, "beginTime"):
            return make_response(constant.RESPONSE_STATUS_FAIL,
                                 constant.RESPONSE_CODE_FAIL,
                                 "param beginTime not exist")
        if not check_request(request, "endTime"):
            return make_response(constant.RESPONSE_STATUS_FAIL,
                                 constant.RESPONSE_CODE_FAIL,
                                 "param endTime not exist")
        begintime = request.json.get("beginTime")
        endtime = request.json.get("endTime")

        pool = current_app.config['bigchain_pool']
        with pool() as unichain:
            avgtime,status = unichain.get_txCreateAvgTimeByRange(begintime, endtime)
        if not status:
            return make_response(constant.RESPONSE_STATUS_FAIL,
                                 constant.RESPONSE_CODE_FAIL,
                                 "response is none")
        avgtime_dict= {'avgTime':avgtime}
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             avgtime_dict)

class ApiBlockCreateAvgTimeByRange(Resource):
    def post(self):
        if not check_request(request, "beginTime"):
            return make_response(constant.RESPONSE_STATUS_FAIL,
                                 constant.RESPONSE_CODE_FAIL,
                                 "param beginTime not exist")
        if not check_request(request, "endTime"):
            return make_response(constant.RESPONSE_STATUS_FAIL,
                                 constant.RESPONSE_CODE_FAIL,
                                 "param endTime not exist")
        begintime = request.json.get("beginTime")
        endtime = request.json.get("endTime")

        pool = current_app.config['bigchain_pool']
        with pool() as unichain:
            avgtime,status = unichain.get_blockCreateAvgTimeByRange(begintime, endtime)
        if not status:
            return make_response(constant.RESPONSE_STATUS_FAIL,
                                 constant.RESPONSE_CODE_FAIL,
                                 "response is none")
        avgtime_dict = {'avgTime':avgtime}
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             avgtime_dict)

class ApiVoteTimeByBlockID(Resource):
    def post(self):
        if not check_request(request, "block_id"):
            return make_response(constant.RESPONSE_STATUS_FAIL,
                                 constant.RESPONSE_CODE_FAIL,
                                 "param block id not exist")
        block_id = request.json.get("block_id")

        pool = current_app.config['bigchain_pool']
        with pool() as unichain:
            avgtime,status = unichain.get_voteTimeByBlockID(block_id)
        if not status:
            return make_response(constant.RESPONSE_STATUS_FAIL,
                                 constant.RESPONSE_CODE_FAIL,
                                 "response is none")
        avgtime_dict = {'avgTime':avgtime}
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             avgtime_dict)

class ApiVoteAvgTimeByRange(Resource):
    def post(self):
        if not check_request(request, "beginTime"):
            return make_response(constant.RESPONSE_STATUS_FAIL,
                                 constant.RESPONSE_CODE_FAIL,
                                 "param beginTime not exist")
        if not check_request(request, "endTime"):
            return make_response(constant.RESPONSE_STATUS_FAIL,
                                 constant.RESPONSE_CODE_FAIL,
                                 "param endTime not exist")
        begintime = request.json.get("beginTime")
        endtime = request.json.get("endTime")

        pool = current_app.config['bigchain_pool']
        with pool() as unichain:
            avgtime,status = unichain.get_voteAvgTimeByRange(begintime, endtime)
        if not status:
            return make_response(constant.RESPONSE_STATUS_FAIL,
                                 constant.RESPONSE_CODE_FAIL,
                                 "response is none")
        avgtime_dict = {'avgTime':avgtime}
        return make_response(constant.RESPONSE_STATUS_SUCCESS,
                             constant.RESPONSE_CODE_SUCCESS,
                             "query success",
                             avgtime_dict)

##Router display
timestat_api.add_resource(ApiTxCreateAvgTimeByRange,
                          '/txCreateAvgTimeByRange',
                          strict_slashes=False)
timestat_api.add_resource(ApiBlockCreateAvgTimeByRange,
                          '/blockCreateAvgTimeByRange',
                          strict_slashes=False)
timestat_api.add_resource(ApiVoteTimeByBlockID,
                          '/voteTimeByBlockID',
                          strict_slashes=False)
timestat_api.add_resource(ApiVoteAvgTimeByRange,
                          '/voteAvgTimeByRange',
                          strict_slashes=False)
