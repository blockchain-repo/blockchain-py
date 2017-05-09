# How to read the json file
import json
from itertools import compress

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
    s = r.table('bigchain').concat_map(lambda doc: doc['block']['transactions'])\
        .filter(r.row["transaction"]["Contract"]["ContractBody"]["ContractId"] == "feca0672-4ad7-4d9a-ad57-83d48db2269b").limit(1) \
        .get_field("transaction").get_field("Contract").run(conn)

    # s = r.table('bigchain').get_all('2e83319bb7377f94a795a098ee626cddcb244fac28d2444d7555ab3feb22bcc8', index='transaction_id')\
    #     .get_field('block').get_field('transactions')[0].get_field('transaction')\
    #     .get_field('conditions')[0][1].update({"isfreeze":True}).run(conn)

    # {"contact": {"phone": {"cell": "408-555-4242"}
    # .update({'isfreeze': True})

    # s = r.table('rewrite').between('', '', index='block_timestamp').get_field('id').run(conn)
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