import logging
import flask
from flask import current_app, request, Blueprint
import uuid
import bigchaindb
from bigchaindb.models import Transaction
import os
import rapidjson

logger = logging.getLogger(__name__)

testVeracity_api = Blueprint('testVeracity_api', __name__)

@testVeracity_api.route('/write_tx/', methods=['POST','GET'])
def createTrans():
    postpid = request.args.get('postpid')
    postcount = request.args.get('postcount')
    createpid = os.getpid()
    pool = current_app.config['bigchain_pool']
    monitor = current_app.config['monitor']
    payload_dict = {}
    createcount = 0
    with pool() as b:
        createcount +=1
        payload_dict['postpid'] = postpid
        payload_dict['createpid'] = createpid
        payload_dict['msg'] = str(uuid.uuid4())
        payload_dict['postcount'] = postcount
        payload_dict['createcount'] = createcount
        tx = Transaction.create([b.me], [b.me], metadata=payload_dict)
        tx = tx.sign([b.me_private])
        rate = bigchaindb.config['statsd']['rate']
        with monitor.timer('write_transaction', rate=rate):
            b.write_transaction(tx)
    tx = tx.to_dict()
    # print(tx['transaction']['metadata']['data']['postcount'], end="-postcount,")
    # print(tx['transaction']['metadata']['data']['createcount'],end="-createcount,")
    return flask.jsonify(**tx)

@testVeracity_api.route('/createtxBypayload/', methods=['POST','GET'])
def createtxBypayload():
    logger.info("[createtxBypayload] received request!!!")
    pool = current_app.config['bigchain_pool']
    monitor = current_app.config['monitor']

    payload_dict = request.get_json(force=True)

    with pool() as b:
        tx = Transaction.create([b.me], [b.me], metadata=payload_dict)
        tx = tx.sign([b.me_private])
        rate = bigchaindb.config['statsd']['rate']
        with monitor.timer('write_transaction', rate=rate):
            b.write_transaction(tx)
    tx = tx.to_dict()
    del payload_dict
    return rapidjson.dumps(tx)

@testVeracity_api.route('get', methods=['POST','GET'])
def getTxByCondetion(conditions):
    pass

def get_error_message(err, type, extra):
    """Useful Function getting the error message to return"""
    error_msg = flask.jsonify({
        'error': err,
        'type': type,
        'extra': extra
    })
    return error_msg
