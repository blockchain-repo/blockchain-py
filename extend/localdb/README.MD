# unichain dir structure

## cluster tables
---
### node_info
```
host=node_ip
public_key=node`s public key
private_key=node`s private key
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
### block_records
```
block_num=block_id
```
---
### vote
```
voting_block_id + '-' + node_pubkey
```

### vote_header
```
current_vote_id=current vote_id
current_vote_timestamp=current vote timestamp
current_vote_num=current block_records count
```
---
