from bigchaindb.web.views import constant
from flask import jsonify
import logging


logger = logging.getLogger(__name__)

def check_request(request, key=None):
    if not request.json:
        return False
    if key and not key in request.json:
        return False
    return True

def make_response(res_status, res_code, res_message=None, res_data=None):
    if not res_status or not res_code:
        res_status = constant.RESPONSE_STATUS_SERVER_ERROR
        res_code = constant.RESPONSE_CODE_SERVER_ERROR
    response = jsonify({
        'status':res_status,
        'code':res_code,
        'message':res_message,
        'data':res_data
    })
    return response

def make_error(status_code, message=None):
    if status_code == 404 and message is None:
        message = 'Not found'
    response_content = {'status': status_code, 'message': message}
    logger.error('HTTP API error: %(status)s - %(message)s', response_content)
    response = jsonify(response_content)
    response.status_code = status_code
    return response
