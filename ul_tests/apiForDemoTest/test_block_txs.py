import rethinkdb as r
import time
rethinkdb_host = '127.0.0.1'
rethinkdb_port = '28015'
rethinkdb_db = 'bigchain'
conn = r.connect(host=str(rethinkdb_host), port=int(rethinkdb_port), db=str(rethinkdb_db))
nowNum = 0
lastNum = 0
while True:
    nowNum = r.table('bigchain').concat_map(lambda doc: doc['block']['transactions']).count().run(conn)
    backNum = r.table('backlog').count().run(conn)
    add = nowNum - lastNum
    lastNum = nowNum
    print("now:",nowNum ,"add:",add,"speed:",add/5,' backlog:',backNum)
    time.sleep(5)

