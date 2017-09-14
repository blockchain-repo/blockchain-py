import rethinkdb as r
import time
rethinkdb_host = '192.168.0.245'
rethinkdb_port = '28015'
rethinkdb_db = 'bigchain'
conn = r.connect(host=str(rethinkdb_host), port=int(rethinkdb_port), db=str(rethinkdb_db))
nowNum = 0
lastNum = 0
nowBackNum = 0
lastBackNum = 0
while True:
    nowNum = r.table('bigchain').concat_map(lambda doc: doc['block']['transactions']).count().run(conn)
    nowBackNum = r.table('backlog').count().run(conn)
    add = nowNum - lastNum
    backAdd = nowBackNum - lastBackNum
    lastNum = nowNum
    lastBackNum = nowBackNum
    print("bigchain::::now:",nowNum ,"add:",add,"speed:",add/5,'------ backlog::::now:',nowBackNum,',add:',backAdd,",speed:",backAdd/5)
    time.sleep(5)