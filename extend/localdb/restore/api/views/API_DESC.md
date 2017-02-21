## node localdb check
### http://127.0.0.1:9986/uniledger/v1/collect/check/ [POST]
request = {
 	"target":"check",
	"desc":"check the node localdb dirs"
    }

response = {
    "free": True,
    "desc": 'can access the node localdb data.'
    }

## node info
### http://127.0.0.1:9986/uniledger/v1/collect/node/ [POST]
request = {
 	"target":"node",
	"desc":"collect node info"
    }

response = {
    'host': '127.0.0.1',
    'block_num': 32,
    "total_block_txs_num":999,
    'pubkey': '7aT6czxEYvucfFWEmPTKggJ2V8iw5fe67rR2YGhVtPuY',
    'vote_num': 49,
    'restart_times': 18
    }

### http://127.0.0.1:9986/uniledger/v1/collect/block/ [POST]
request = {
 	"target":"block",
 	"current_block_num":1,
	"desc":"collect node info"
    }

response = {
    "host":host,
    "block_num": block_num,
    "total_block_num": total_block_num,
    "block_txs": block_txs,
    "accumulate_block_txs": accumulate_block_txs,
    "total_block_txs_num": total_block_txs_num,
    "block_id":block_id,
    "block": block,
    "votes": block_votes,
    "votes_count": len(block_votes),
    "desc": "The node block_num {}, progress {:<8},".format(block_num,"%0.2f%%" %(block_num/total_block_num*100))
    }

### http://127.0.0.1:9986/uniledger/v1/collect/pre_restore/ [POST]
request = {
     "target":'pre_restore':
      "sent_num":0,
      "db":bigchian,
      "clear":True, # if confidition is ok, clear the data
      "fore_clear":True, # force clear the data and reset restore_header
      "desc":''
    }

response = {
    "exist_db":True,
    "records_count":1 or 10,
    "need_init":True or False, # init and clear use fab init_unichain
    "reset_sent":True, # if True, reset the restore_header
    "desc":''
    }

### http://127.0.0.1:9986/api/v1/collect/rethinkdb/ [POST]
request = {
    "target": type,
    "desc": desc,
    "current_block_num":num,
    "block":block,
    "votes":votes
    }

response = {
    "op":'insert',
    "success":insert_flag,
    "msg":fail_msg
    }
