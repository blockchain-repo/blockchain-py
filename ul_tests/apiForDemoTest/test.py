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
    s = r.table("bigchain").order_by(index=r.desc('block_timestamp')).map({'id':r.row['id'],'count':r.row['block']['transactions'].count()}).limit(10).run(conn)
    # r.db('bigchain').table('bigchain').limit(20).map(id: row('id'), signature: row('signature'), len: row('block')('transactions').count()};
    # for i in s:
    #     id = i['id']
    #     l = len(i['transactions'])
    #     print(l)
    print(s)

get_txNumberById("e5ff34ef72fd80e839512652c4a9c55764e648590a05c5feb88610a6a5e0e491")

# -----------------------------------
# r.table('rewrite').index_create('block_timestamp',r.row['timestamp']).run(conn)
# -----------------------------------
# r.table('bigchain').index_create('tx_timestamp', r.row['block']['transactions']['transaction']['timestamp']).run(conn)
