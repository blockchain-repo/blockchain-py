import rethinkdb as r
import sys
import subprocess

rethinkdb_host = subprocess.getoutput("cat press_tool_write.sh |grep \"rethinkdb_host=\"|awk -F\"=\" '{print $2}'")
rethinkdb_port = subprocess.getoutput("cat press_tool_write.sh |grep \"rethinkdb_port=\"|awk -F\"=\" '{print $2}'")
rethinkdb_db = subprocess.getoutput("cat press_tool_write.sh |grep \"rethinkdb_db=\"|awk -F\"=\" '{print $2}'")
conn = r.connect(host=str(rethinkdb_host), port=int(rethinkdb_port), db=str(rethinkdb_db))
vote_valid_num = subprocess.getoutput("cat press_tool_write.sh |grep \"chain_node_num=\"|awk -F\"=\" '{print $2}'")
vote_valid_num = int(vote_valid_num) / 2

begin_timestamp = sys.argv[1]
end_timestamp = sys.argv[2]
transaction_sum = 0

block_ids = r.table('votes').between(begin_timestamp, end_timestamp, index='vote_timestamp').get_field('vote').group('voting_for_block').count().run(conn)
for block_id in block_ids:
#    print (block_id, block_ids[block_id])
    if block_ids[block_id] >= int(vote_valid_num):
        block_txs = r.table('bigchain').get(block_id).get_field('block').get_field('transactions').count().run(conn)
        transaction_sum = transaction_sum + block_txs
print (transaction_sum)
