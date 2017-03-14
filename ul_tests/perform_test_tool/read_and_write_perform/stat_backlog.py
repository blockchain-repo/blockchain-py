import rethinkdb as r
import sys
import subprocess

rethinkdb_host = subprocess.getoutput("cat press_tool_read_and_write.sh |grep \"rethinkdb_host=\"|awk -F\"=\" '{print $2}'")
rethinkdb_port = subprocess.getoutput("cat press_tool_read_and_write.sh |grep \"rethinkdb_port=\"|awk -F\"=\" '{print $2}'")
rethinkdb_db = subprocess.getoutput("cat press_tool_read_and_write.sh |grep \"rethinkdb_db=\"|awk -F\"=\" '{print $2}'")
conn = r.connect(host=str(rethinkdb_host), port=int(rethinkdb_port), db=str(rethinkdb_db))

transaction_sum = r.table('backlog').count().run(conn)
print (transaction_sum)
