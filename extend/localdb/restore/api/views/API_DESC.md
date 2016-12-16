## node localdb check
### http://127.0.0.1:9986/api/v1/collect/check/ post
request=
{
 	"target":"check",
	"desc":"check the node localdb dirs"
}

response = {
    "free": True,
    "desc": 'can access the node localdb data.'
}

## node info
### http://127.0.0.1:9986/api/v1/collect/node/ post
request=
{
 	"status":"start",
 	"target":"node",
	"desc":"collect node info"
}

response=
{
    'host': '127.0.0.1',
    'block_num': 32,
    'pubkey': '7aT6czxEYvucfFWEmPTKggJ2V8iw5fe67rR2YGhVtPuY',
    'vote_num': 49,
    'restart_times': 18
}


### http://127.0.0.1:9986/api/v1/collect/block/ post
request=
{
 	"status":"start",
 	"target":"block",
 	"current_block_num":1,
	"desc":"collect node info"
}

response = {
    "block_num": block_num,
    "total_block_num": total_block_num,
    "block_id":block_id,
    "block": block,
    "votes": block_votes,
    "votes_count": len(block_votes),
    "desc": "The node block_num {}, progress {:<8},".format(block_num,"%0.2f%%" %(block_num/total_block_num*100))
}