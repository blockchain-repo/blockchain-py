from bigchaindb.web.views import constant
from flask import jsonify

def check_request(request, key=None):
    if not request.json:
        return False
    if key and not key in request.json:
        return False
    return True

def make_response(res_status, res_code, res_message=None, res_data=None):
    if not res_status or not res_code:
        res_status = constant.RESPONSE_STATUS_FAIL
        res_code = constant.RESPONSE_CODE_FAIL
    response = jsonify({
        'status':res_status,
        'code':res_code,
        'message':res_message,
        'data':res_data
    })
    return response

print(constant.RESPONSE_STATUS_FAIL)

