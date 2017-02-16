import logging
import flask
from flask import current_app, request, Blueprint
from bigchaindb.web.views.base import make_error
import bigchaindb
from bigchaindb.models import Transaction
import os
import rapidjson

logger = logging.getLogger(__name__)

common_api = Blueprint('common_api', __name__)

#
# # 单条payload创建交易
# @common_api.route('/createTxByPayload/', methods=['POST'])
# def createTxByPayload():
#     pool = current_app.config['bigchain_pool']
#     monitor = current_app.config['monitor']
#
#     payload_dict = request.get_json(force=True)
#
#     with pool() as b:
#         tx = Transaction.create([b.me], [b.me], metadata=payload_dict)
#         tx = tx.sign([b.me_private])
#         rate = bigchaindb.config['statsd']['rate']
#         with monitor.timer('write_transaction', rate=rate):
#             b.write_transaction(tx)
#
#     # tx = tx.to_dict()
#     # return rapidjson.dumps(tx)
#     return tx.to_dict()


# # 根据交易ID获取交易
# @common_api.route('/getTxById/', methods=['POST'])
# def getTxById():
#     tx_id = request.args.get('tx_id')
#     pool = current_app.config['bigchain_pool']
#     with pool() as b:
#         tx = b.get_transaction(tx_id)
#
#     if not tx:
#         return make_error(404)
#
#     return tx.to_dict()

#
# # 根据区块ID获取区块
# @common_api.route('/getBlockById/', methods=['POST'])
# def getBlockById():
#     block_id = request.args.get('block_id')
#     pool = current_app.config['bigchain_pool']
#     with pool() as b:
#         block = b.get_block(block_id)
#
#     if not block:
#         return make_error(404)
#
#     return block.to_dict()

#
# # 根据区块ID获取区块中的交易
# @common_api.route('/getAllTxsFromBlock/', methods=['POST'])
# def getAllTxsFromBlock(block_id):
#     block_id = request.args.get('block_id')
#     pool = current_app.config['bigchain_pool']
#     with pool() as b:
#         block = b.get_block(block_id)
#
#     if not block:
#         return make_error(404)
#     # TODO check
#     txList = block['transactions']
#     return txList.to_dict()
#
#
# # 根据区块ID获取区块中的交易条数
# @common_api.route('/getTxNumberInBlock/', methods=['POST'])
# def getTxNumberInBlock():
#     block_id = request.args.get('block_id')
#     pool = current_app.config['bigchain_pool']
#     with pool() as b:
#         number = b.get_txNumber(block_id)
#     return number


# # 获取区块链中的总交易条数
# @common_api.route('/getTxNumberInUnichain/', methods=['POST'])
# def getTxNumberInUnichain():
#     pool = current_app.config['bigchain_pool']
#     with pool() as b:
#         number = b.get_txNumber()
#     return number


# # 获取区块链中的总区块数
# @common_api.route('/getBlockNumberInUnichain/', methods=['POST'])
# def getBlockNumberInUnichain():
#     pool = current_app.config['bigchain_pool']
#     with pool() as b:
#         number = b.get_BlockNumber()
#     return number


# # 获取所有无效区块集
# @common_api.route('/getInvalidBlcok/', methods=['POST'])
# def getInvalidBlcok():
#     pool = current_app.config['bigchain_pool']
#     with pool() as b:
#         invalidBlockIdList = b.get_invalidBlockIdList()
#     return invalidBlockIdList


# # 获取指定时间区间内的无效区块集
# @common_api.route('/getInvalidBlcokByTime/', methods=['POST'])
# def getInvalidBlcokByTime():
#     startTime = request.args.get('startTime')
#     endtime = request.args.get('endtime')
#     pool = current_app.config['bigchain_pool']
#     with pool() as b:
#         invalidBlockIdList = b.get_invalidBlockIdList(startTime,endtime)
#     return invalidBlockIdList


# # 获取参与投票的节点公钥集
# @common_api.route('/getAllPublicKey/', methods=['POST'])
# def getAllPublicKey():
#     pool = current_app.config['bigchain_pool']
#     with pool() as b:
#         pubkeyList = b.get_allPublicKey()
#     return pubkeyList

#============================================

# # 根据指定时间区间获取区块集
# @common_api.route('/getBlocksByTime/', methods=['POST'])
# def getBlocksByTime():
#     startTime = request.args.get('startTime')
#     endtime = request.args.get('endtime')
#     pool = current_app.config['bigchain_pool']
#     with pool() as b:
#         blockIdList = b.get_BlockIdList(startTime=startTime,endtime=endtime)
#     return blockIdList


# # 根据指定时间区间获取交易集
# @common_api.route('/getTxsByTime/', methods=['POST'])
# def getTxsByTime():
#     startTime = request.args.get('startTime')
#     endtime = request.args.get('endtime')
#     pool = current_app.config['bigchain_pool']
#     with pool() as b:
#         txIdList = b.get_TxIdByTime(startTime,endtime)
#     return txIdList

#
# # 获取每区块中包含的交易条数
# @common_api.route('/getTxNumOfAllBlock/', methods=['POST'])
# def getTxNumOfAllBlock():
#     pool = current_app.config['bigchain_pool']
#     with pool() as b:
#         blockIdTxList = b.get_txNumberOfAllBlock()
#     return blockIdTxList


def get_error_message(err, type, extra):
    """Useful Function getting the error message to return"""
    error_msg = flask.jsonify({
        'error': err,
        'type': type,
        'extra': extra
    })
    return error_msg
