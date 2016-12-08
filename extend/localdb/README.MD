# unichain dir structure

## localdb dirs
---
### node_info
```
host=node_ip
public_key=node`s public key
private_key=node`s private key
restart_times=0
```
---
### block
```
block_id=block
```
### block_header
```
genesis_block_id=genesis block id
current_block_id=current block_id
current_timestamp=current block timestamp
current_block_num=current block_records count
```
---
```
恢复的时候根据block_num恢复,因为同一个块的previous block
可能不同,根据votes恢复可能会出现大量重复,循环查找问题!
```
### block_records
```
block_num=block_id
```
---
```
votes 可能会出现,对同一块的投票时间戳相差很大[比如:如果
新增节点的话,会对所有块,本节点为投票的进行投票,时间戳就是
当前投票的,其他节点的投票可能是很久以前的]所以节点信息,
应尽可能保持不变!
```
### vote
```
previous_block_id + '-' + node_pubkey
```

### vote_header
```
current_vote_id=current vote_id
current_vote_timestamp=current vote timestamp
current_vote_num=current block_records count
```
---