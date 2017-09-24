# How to read the json file
import json
from itertools import compress
from bigchaindb import util
# # open file
# f = open("./keypair.json", "r")
# # load data
# keypairAll = json.load(f)
#
# # get public_key
# owner_before = keypairAll["keypair"][0]["public_key"]
# print(owner_before)
#
# owner_after = keypairAll["keypair"][1]["public_key"]
# print(owner_after)

# vote_cast = [False]
# vote_validity = [True]
# vote_list = list(compress(vote_cast, vote_validity))
# print(vote_list)


import datetime
import time

# print(str(round(time.time())))
# print(str(round(time.time() * 1000)))
# print(datetime.datetime.now())
# print(datetime.datetime.now().microsecond)


import  rethinkdb as r
import bigchaindb as b

def get_txNumberById(block_id):
    conn = r.connect(db='bigchain')
    # s = r.table('bigchain').get_field('block').get_field('transactions').get_field('').run(conn)
    # s = r.table('bigchain').get(block_id).get_field('block').get_field('transactions').run(conn)

    # s = r.expr(r.db('bigchain').table('bigchain').concat_map(lambda bigchain:r.table('bigchain')).count()).run(conn)
    #s = r.table('bigchain').get_all('e5ff34ef72fd80e839512652c4a9c55764e648590a05c5feb88610a6a5e0e491', index='id').concat_map(lambda block: block['block']['transactions']).count().run(conn)


    # s = r.table('rewrite').between('0', r.maxval,index='block_timestamp').get_field('id').run(conn)
    # for item in s:
    #     print("The {}th is: {}".format(item))
    # s = r.table('bigchain').between('0', r.maxval, index='block_timestamp').order_by(index=r.desc('block_timestamp')).get_field('id').run(conn)
    # r.table('bigchain').index_create('tx_timestamp', r.row['block']['transactions']['transaction']['timestamp']).run(conn)
    # s = r.table('bigchain').concat_map(lambda block: block['block']['transactions']).run(conn)

    # s = r.table('bigchain').concat_map(lambda block: block['block']['transactions']).filter(lambda tx: tx['transaction']['timestamp'] > '1487076389680' & tx['transaction']['timestamp'] <'1487076389679').run(conn)
    # s = r.table('bigchain').concat_map(lambda block: block['block']['transactions']).filter(lambda tx: tx['transaction']['timestamp'] == '1487076389679').count().run(conn)
    # s = r.table('bigchain').concat_map(lambda block: block['block']['transactions']).order_by(lambda tx: tx['transaction']['timestamp']).run(conn)
    # for item in s:
    #     print(item)
    # s = r.table("bigchain").concat_map(lambda block: block['block']['transactions']).order_by(r.asc(r.row['block']['transactions']['transaction']['timestamp'])).filter((r.row["transaction"]['timestamp'] < '1487076389680') & (r.row["transaction"]['timestamp'] > '1487076389678')).run(conn)
    # r.table('users').get(10001).pluck({'contact': {'phone': 'work'}}
    # s = r.table("bigchain").with_fields('id':r.row['block']['transactions']).run(conn)
    # s = r.table("bigchain").order_by(index=r.desc('block_timestamp')).map({'id':r.row['id'],'count':r.row['block']['transactions'].count()}).limit(10).run(conn)
    # r.db('bigchain').table('bigchain').limit(20).map(id: row('id'), signature: row('signature'), len: row('block')('transactions').count()};
    # for i in s:
    #     id = i['id']
    #     l = len(i['transactions'])
    #     print(l)

    # s = r.table('bigchain').between('1487230111131', '1487230111830', index='tx_timestamp').run(conn)  # tx time
    # s = r.table('bigchain').get_field('block').get_field('transactions').run(conn)
    #s = r.table("bigchain").concat_map(lambda block: block['block']['transactions']).filter((r.row["transaction"]['timestamp'] > '1487230111131') & (r.row["transaction"]['timestamp'] < '1487230111831')).count().run(conn)
    #s = r.table('bigchain').between('1487230111131', '1487230112918', index='block_timestamp').count().run(conn)
    # s = r.table('bigchain').get_all(block_id, index='id').run(conn)
    # s = r.table('bigchain').get_all(block_id, index='id').get_field('block').get_field('timestamp').run(conn)
    # s = r.table('votes').filter(r.row['vote']['voting_for_block'] == block_id).max(r.row['vote']['timestamp']).get_field('vote').get_field('timestamp').run(conn)
    # s = r.table('votes').between('0', '1', index='block_and_voter').get_field('vote').get_field('voting_for_block').distinct().count().run(conn)
    # s = r.table('bigchain').get_all(block_id, index='id').get_field('block').get_field('transactions').run(conn)
    # s = r.table("bigchain").concat_map(lambda block: block['block']['transactions']).order_by(r   .desc(r.row['block']['transactions']['transaction']['timestamp'])).filter((r.row["transaction"]['timestamp'] >= '1487313303289') and (r.row["transaction"]['timestamp'] <= '1487313304289')).run(conn)
    # s = r.table("bigchain").between('1487313303288', '1487313304299', index='tx_timestamp').get_field('block').get_field('transactions').run(conn)
    # s = r.table('bigchain').get_all('39d8d3d29554d209a1283b20a1e3e198bdd27c099b8df9042195d7bb0728219f', index='transaction_id').run(conn)

    pubkey = 'Gvexu49oskc6ptYwzqP9q8sL9jLxjNZNMBWgVVhUtPmD'
    #s = r.table('bigchain').concat_map(lambda doc: doc['block']['transactions'])\
        # .filter(lambda tx: (tx['transaction']['conditions'].contains(lambda c: c['owners_after'].contains(pubkey)))
        #                 or (tx['transaction']['fulfillments'].contains(lambda f: f['owners_before'].contains(pubkey))))\
        # .order_by(r.row['timestamp']).map({'id':r.row['id'],'owner_before':r.row['transaction']['fulfillments']['owners_before'],'operation':r.row['transaction']['operation'],'conditions':r.row['transaction']['conditions'],'timestamp':r.row['transaction']['timestamp']}).run(conn)
    owner = '5XAJvuRGb8B3hUesjREL7zdZ82ahZqHuBV6ttf3UEhyL'
    # s = r.table('bigchain').concat_map(lambda doc: doc['block']['transactions'])\
    #     .filter(lambda tx: tx['transaction']['conditions'].contains(lambda c: c['owners_after'].contains(owner))).run(conn)
    contract_id = 'feca0672-4ad7-4d9a-ad57-83d48db2269b'
    taskId = 'taskId'
    taskNUm = 0
    5

    # s = r.table('bigchain').concat_map(lambda doc: doc['block']['transactions']).filter(r.row["transaction"]["operation"]=="CONTRACT")\
    #     .filter(r.row["transaction"]["Contract"]["ContractBody"]["ContractId"] == contract_id ) \
    #     .get_field("transaction").get_field("Contract").run(conn)
    # s = r.table('bigchain').concat_map(lambda doc: doc['block']['transactions']).filter(lambda tx: tx['transaction']['Relation']['ContractId']=='feca0672-4ad7-4d9a-ad57-83d48db2269b') \
    #             .filter(lambda tx: tx['transaction']['Relation']['TaskId'] == 'taskId').filter(lambda tx: tx['transaction']['Relation']['TaskExecuteIdx'] == 0)\
    #     .filter(lambda tx: tx['transaction']['conditions'].contains(lambda c: c['owners_after'].contains(owner))).run(conn)

    # s = r.table('bigchain').get_all('126ff745192eea5873fe0b18559035e06a360e57785083579889bfaaa254b0ca', index='transaction_id').run(conn)

    # print(r.table('bigchain' ).concat_map(lambda doc: doc['block']['transactions'])\
    #     .filter( lambda tx: tx['transaction']['Relation']['ContractId'] == contract_id)\
    #     .filter(lambda tx: tx['transaction']['Relation']['TaskId'] == taskId)\
    #     .filter( lambda tx: tx['transaction']['Relation']['TaskExecuteIdx'] == taskNUm)\
    #     .filter(lambda tx: tx['transaction']['conditions'].contains(lambda c: c['owners_after'].contains(owner))))
    # s = r.table('bigchain',read_mode='majority').concat_map(lambda doc: doc['block']['transactions'])\
    #     .filter( lambda tx: tx['transaction']['Relation']['ContractId'] == contract_id)\
    #     .filter(lambda tx: tx['transaction']['Relation']['TaskId'] == taskId)\
    #     .filter( lambda tx: tx['transaction']['Relation']['TaskExecuteIdx'] == taskNUm)\
    #     .filter(lambda tx: tx['transaction']['conditions'].contains(lambda c: c['owners_after'].contains(owner))).run(conn)
    contract_hash_id = '63841426ea1c501745d56ce47a4e7b93bf85841d54f2c77102ce488ac0ce8b51'
    # s = r.table('bigchain').concat_map(lambda doc: doc['block']['transactions']).filter(lambda tx: tx['transaction']['Relation']['ContractHashId']==contract_hash_id).run(conn)
    # s = r.table('bigchain').concat_map(lambda doc: doc['block']['transactions'])\
    #     .filter({'transaction':{'operation':'METADATA'}}) \
    #     .filter(lambda tx: tx['transaction']['metadata']['data']['goodsinfo'].contains(lambda gi: gi['itemTitle']=="测试-苹果（含新版规格）")) \
    #     .get_field("transaction").get_field("metadata").get_field('data').order_by('timestamp') \
    #     .filter((r.row['timestamp'] >= '1499759100000') & (r.row['timestamp'] <= '1499759109000')) \
    #     .slice(0,2)\
    #     .run(conn)
    # s = r.table('bigchain').concat_map(lambda doc: doc['block']['transactions'])\
    #                     .filter({'transaction': {'metadata': {'data':{'orderCode': 'D1707111643542395'}}}})\
    #                     .get_field("transaction").get_field("metadata").get_field('data').order_by('timestamp')\
    #                     .filter((r.row['timestamp'] >= '1499702400000') & (r.row['timestamp'] <= '1499788800000')).run(conn)
    # s = r.table('bigchain').concat_map(lambda doc: doc['block']['transactions'])\
    #         .filter({'transaction': {'operation': 'METADATA'}})\
    #         .filter(lambda tx: tx['transaction']['metadata']['data']['goodsinfo'].contains(lambda gi: gi['itemTitle'] == '测试-苹果（含新版规格）')) \
    #         .get_field("transaction").get_field("metadata").get_field('data').get_field('orderCode').run(conn)

    # lambda doc:   .filter((r.row['timestamp'] >= '1499765383000'))\
    # r.expr(["Peter", "John"])
    # .contains(doc["name"])
    # r.table('bigchain').concat_map(lambda doc: doc['block']['transactions'])
    # .filter({'transaction': {'operation': 'METADATA'}})
    # .get_field("transaction").get_field("metadata").get_field('data').order_by('timestamp')
    # .filter((r.row['timestamp'] >= startTime) & (r.row['timestamp'] <= endTime))
    # .filter(r.row['orderType'] == 2).slice(startIndex, endIndex))

    orderCodeList = ['D1707141404012364', 'S1707111549432395', 'D1707071325172395', 'D1707111545242395', 'D1707111610442394', 'D1707111723592395', 'D1707111544292395', 'S1707141401422364', 'D1707141404062364', 'S1707111602422395', 'D1707111545182395', 'D1707111545142395', 'D1707111644142395', 'S1707111731432395', 'S1707111722422395', 'D1707111643542395', 'S1707111619422394', 'D1707111517032394', 'S1707141406422364', 'D1707141401052364', 'D1707111723502395', 'S1707111725422395', 'S1707111700422395', 'D1707141401122364', 'D1707111610362394', 'D1707111643492395', 'S1707141105422364', 'D1707111644092395', 'D1707111542212395', 'D1707071407472387', 'D1707111545092395', 'S1703050106442156', 'S1707111658432395', 'D1707111724252395', 'S1707111457432395', 'S1707111709422395', 'S1707111549432395', 'S1707111729432395', 'D1707111545002395', 'D1707141103162364', 'S1707111459422395', 'S1707141402422364', 'D1707111542192395', 'D1707111545392395', 'S1707111727422395', 'D1707111643212395', 'S1707111620432394', 'D1707111724042395', 'D1707111643152395', 'S1707111628422394', 'S1707111707422395', 'D1707111644032395', 'S1707111708422395', 'S1707111701422395', 'D1707111545042395', 'D1707111643442395', 'S1707111712422395', 'D1707111643402395', 'D1707141030372364', 'S1707111705422395', 'D1707111617432395', 'D1707111544402395', 'D1707111544162395', 'S1707111721432395', 'D1707111724082395']
    # s = r.table('bigchain').concat_map(lambda doc: doc['block']['transactions']) \
    #     .filter(lambda doc: r.expr(orderCodeList) .contains(doc['transaction']['metadata']['data']['orderCode']))\
    #     .get_field("transaction").get_field("metadata").get_field('data').order_by('timestamp') \
    #     .filter((r.row['timestamp'] >= '1499765383000') & (r.row['timestamp'] <= '1499765383000')).filter(r.row['orderType'] == 2).slice(0, 5)\
    #     .run(conn)
    node_name = "1"
    # s = r.table('backlog' + node_name).insert("").run(conn)

    # s = r.table('backlog').get_all(['5mVrPtqUzXwKYL2JeZo4cQq2spt8qfGVx3qE2V7NqgyU', False], index='assignee_assignee_isdeal').update({'assignee_isdeal': True}, return_changes=True).run(conn)

    # s = r.table('backlog').get('1c424db85c402af3eeb0fb4a8f87a4f27a5a3766c4550bbedcbe4f40f7eabb0b').get_field('node_name').run(conn)
    # print(s == "backlog5mVrP")

    # .
    # node_pubkey = "5mVrPtqUzXwKYL2JeZo4cQq2spt8qfGVx3qE2V7NqgyU"
    # unvoted = r.table('bigchain')\
    #     .filter(lambda block: r.table('votes').get_all([block['id'], node_pubkey], index='block_and_voter').is_empty())\
    #     .order_by(r.asc(r.row['block']['timestamp']))\
    #     .run(conn)
    # print(unvoted)
    # unvoted_blocks2 = filter(lambda block: util.need_vote_block(block,node_pubkey), unvoted)
    # for element in unvoted_blocks2:
    #     print("key:",element)
    # s = r.table('bigchain').concat_map(lambda doc: doc['block']['transactions'])\
    #     .filter({'transaction': {'metadata': {'data': {'orderCode': 'S1707111712422395'}}}})\
    #     .get_field("transaction").get_field("metadata").get_field('data')\
    #     .concat_map(lambda goods: goods['goodsinfo']).get_field('itemTitle').run(conn)
    # s = r.table('bigchain').concat_map(lambda doc: doc['block']['transactions'])\
    # .filter({'transaction': {'metadata': {'data': {'orderCode': 'S1707111712422395'}}}})\
    # .get_field("transaction").get_field("metadata").get_field('data').limit(1).run(conn)
# == '测试-苹果（含新版规格）'
# .filter({'transaction': {'metadata': {'data': {'from': {'userName': '供应商户01责任有限公司'}}}}}) \
#     .get_field("transaction").get_field("metadata").get_field('data').order_by('timestamp') \
#     .filter((r.row['timestamp'] >= '1499759100000') & (r.row['timestamp'] <= '1499759109000')) \
    # s = r.table('bigchain').get_all('2e83319bb7377f94a795a098ee626cddcb244fac28d2444d7555ab3feb22bcc8', index='transaction_id')\
    #     .get_field('block').get_field('transactions')[0].get_field('transaction')\
    #     .get_field('conditions')[0][1].update({"isfreeze":True}).run(conn)

    # {"contact": {"phone": {"cell": "408-555-4242"}
    # .update({'isfreeze': True})

    # s = r.table('rewrite').between('', '', index='block_timestamp').get_field('id').run(conn)
    # print(unvoted)
    # print(unvoted_blocks1)
    # print(unvoted_blocks2)


    di = {'state': 1, 'roleID': 1, 'name': '张三1', 'validFlag': True}

    # s = r.table('bigchain').concat_map(lambda doc: doc['block']['transactions'])\
    #     .filter({'transaction': {'metadata': {'data': {'username': 'zhangsan'}}}})\
    #     .get_field("transaction").get_field("metadata").get_field('data').order_by(r.desc(r.row['timestamp'])).run(conn)
    # s = r.table('bigchain')\
    #     .concat_map(lambda doc: doc['block']['transactions'])\
    #     .filter(lambda tx: tx['transaction']['conditions'].contains(
    #     lambda c: c['owners_after'].contains('EXJqxCeYNMxYriTKsdxHFHAJ4Qtm6Qn5gif1zpQkrtvN'))).run(conn)
    transaction_id = '6a289cf22dee7cdeb8b15176379dc82ba7976dde2ee795e667ac53fad7849c69'
    s = r.table('bigchain').filter(lambda txt: txt['block']['transactions']['id'].contains(transaction_id)).run(conn)
    print(s)


get_txNumberById("39d8d3d29554d209a1283b20a1e3e198bdd27c099b8df9042195d7bb0728219f")

# -----------------------------------
# r.table('rewrite').index_create('block_timestamp',r.row['timestamp']).run(conn)
# -----------------------------------
#
# r.table('bigchain').index_create('tx_timestamp', r.row['block']['transactions']['transaction']['timestamp']).run(conn)


# from bigchaindb.common.util import gen_timestamp
# print(isinstance(gen_timestamp(),str))
# from flask import jsonify
# avgtime_d= {'avgtime':'q'}
# s = jsonify({
#         'status':'1',
#         'data':avgtime_d
#     })
# print(s)