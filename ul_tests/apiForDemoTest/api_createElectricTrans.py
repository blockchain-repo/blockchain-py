import json
import requests
import rapidjson
from bigchaindb.common.crypto import hash_data, VerifyingKey, SigningKey
from bigchaindb.common.util import gen_timestamp, serialize
import bigchaindb
# # url='http://192.168.159.100:9984/uniledger/v1/block/queryByID/'
# values = {
#                 "block_id": "f41591dbc01c5a7f016dc43c0044ab6f9e93e21e378ed147e91f66ae75e2b638"
#             }


# url='http://192.168.159.100:9984/uniledger/v1/block/queryTxsByID/'
#
# values = {
#                 "block_id": "f41591dbc01c5a7f016dc43c0044ab6f9e93e21e378ed147e91f66ae75e2b638"
#             }
#
# url='http://192.168.159.100:9984/uniledger/v1/block/queryTxsCountByID/'
#
# values = {
#                 "block_id": "f41591dbc01c5a7f016dc43c0044ab6f9e93e21e378ed147e91f66ae75e2b638"
#             }

# url='http://192.168.159.100:9984/uniledger/v1/block/queryBlockCount/'

# url='http://192.168.159.100:9984/uniledger/v1/block/queryBlocksByRange/'
#
# values = {
#                 "startTime":"1483689947",
#                 "endTime": "1487230112918"
#             }

# url='http://127.0.0.1:9984/uniledger/v1/block/queryInvalidBlockTotal/'


# url='http://127.0.0.1:9984/uniledger/v1/block/queryInvalidBlockByRange/'
#
# values = {
#                 "beginTime":"1487230113051",
#                 "endTime": "1487230113055"
#             }


#vote=========================
# url='http://192.168.159.100:9984/uniledger/v1/vote/publickeySet/'


#timestat=========================
# url='http://192.168.159.100:9984/uniledger/v1/timestat/txCreateAvgTime'
# values = {
#                 "begintime":"1487230111131",
#                 "endtime": "1487230112918"
#             }


# url='http://192.168.159.100:9984/uniledger/v1/timestat/blockCreateAvgTime'
# values = {
#                 "begintime":"1487230111131",
#                 "endtime": "1487230112918"
#             }
#
# url='http://192.168.159.100:9984/uniledger/v1/timestat/voteTimeByBlockID'
# values = {
#                 "id": "93a2a544eb0971c8b0a910afa22b638437fc85fe10cdd2537a3872c03cce7be7"
#             }

# url='http://36.110.115.195:38/uniledger/v1/timestat/voteTimeAvgTime'
# values = {
#                 "beginTime":"0",
#                 "endTime": "1487396838848"
#             }

# url='http://36.110.115.195:38/uniledger/v1/timestat/voteTimeAvgTime'
# values = {
#                 "beginTime":"0",
#                 "endTime": "1487396838848"
#             }

# url='http://127.0.0.1:9984/uniledger/v1/transaction/queryByID/'
# values = {
#                 "tx_id": "39d8d3d29554d209a1283b20a1e3e198bdd27c099b8df9042195d7bb0728219f",
#                 "type":"1"
#             }

# url='http://127.0.0.1:9984/uniledger/v1/condition/getAsset?unspent=true&public_key={}'.format('6GSFmL4kcK6YJVFC2xq1KegmezhMRNhXLGmRAkLEt9Zq')
# values = {
#                 "public_key": "",
#                 "unspent":True
#             }


#alice create tx
# url='http://127.0.0.1:9984/uniledger/v1/transaction/createByPayload/'
url='http://127.0.0.1:9984/uniledger/v1/contract/createContractTx/'

# values =

# url='http://127.0.0.1:9984/uniledger/v1/transaction/getTxRecord?public_key={}'.format('Gvexu49oskc6ptYwzqP9q8sL9jLxjNZNMBWgVVhUtPmD')


#
# r=requests.get(url)
#
# print(r.text)
#



headers = {
  'Content-Type': 'application/json'
}
# print(values)
# s = rapidjson.dumps(values, skipkeys=False, ensure_ascii=False,  sort_keys=True)
# print(s)
# s = rapidjson.loads('{"id":"56c6a6780abd76bd486d3abe63f2266318bd83be0f913521adbb961944c04f3f","transaction":{"Contract":{"ContractBody":{"Caption":"","Cname":"star","ContractAssets":null,"ContractComponents":null,"ContractId":"","ContractOwners":["qC5zpgJBqUdqi3Gd6ENfGzc5ZM9wrmqmiPX37M9gjq3","J2rSKoCuoZE1MKkXGAvETp757ZuARveRvJYAzJxqEjoo"],"ContractSignatures":null,"ContractState":"","Creator":"","CreatorTime":"","Ctype":"","Description":"","EndTime":"","StartTime":""},"ContractHead":{"MainPubkey":"qC5zpgJBqUdqi3Gd6ENfGzc5ZM9wrmqmiPX37M9gjq3","Version":1},"id":"3ea445410f608e6453cdcb7dbe42d57a89aca018993d7e87da85993cbccc6308"},"Relation":{"ContractId":"834fbab3-9118-45a5-b6d4-31d7baad5e13","TaskId":"","Voters":["qC5zpgJBqUdqi3Gd6ENfGzc5ZM9wrmqmiPX37M9gjq3","J2rSKoCuoZE1MKkXGAvETp757ZuARveRvJYAzJxqEjoo"],"Votes":[{"NodePubkey":"qC5zpgJBqUdqi3Gd6ENfGzc5ZM9wrmqmiPX37M9gjq3","Signature":"65D27HW4uXYvkekGssAQB93D92onMyU1NVnCJnE1PgRKz2uFSPZ6aQvid4qZvkxys7G4r2Mf2KFn5BSQyEBhWs34","Vote":{"InvalidReason":"","IsValid":true,"Timestamp":"1493261777831","VoteFor":"7fb5daf3548c2d0d9b71ce25ee962d164cbb87d82078d7361b8424a95c7c4b94","VoteType":"None"},"id":"320abad9-7134-40e0-9152-176e5d3c10be"},{"NodePubkey":"J2rSKoCuoZE1MKkXGAvETp757ZuARveRvJYAzJxqEjoo","Signature":"5i5dTtQseQjWZ8UdchqQtgttyeeFmB3LDFYzNKafvV2YvTqwv4wZ9mFsH7qgysV9ow893D1h2Xnt1uCXLHtbKrkT","Vote":{"InvalidReason":"","IsValid":true,"Timestamp":"1493261777831","VoteFor":"7fb5daf3548c2d0d9b71ce25ee962d164cbb87d82078d7361b8424a95c7c4b94","VoteType":"None"},"id":"ed116223-f218-4465-a1bc-8c9de6fd51de"}]},"asset":null,"conditions":null,"fulfillments":null,"metadata":{"data":{"a":"1","b":"2","c":"3"},"id":"meta-data-id"},"operation":"OUTPUT","timestamp":"1493261777831"},"version":1}')
# print(s)
# s = rapidjson.dumps(s, skipkeys=False, ensure_ascii=False,  sort_keys=True)
# print(s)


msg = "hello unichain 2017"
pri = "5Pv7F7g9BvNDEMdb8HV5aLHpNTNkxVpNqnLTQ58Z5heC"
signing_key = SigningKey(pri)
signature = signing_key.sign(serialize(msg).encode()).decode()
print(signature)

public_key = signing_key.get_verifying_key().encode()
print(public_key)



detail_serialized = serialize(msg).encode()
verifying_key = VerifyingKey("3FyHdZVX4adfSSTg7rZDPMzqzM8k5fkpu43vbRLvEXLJ")
s = verifying_key.verify(detail_serialized, signature)
print(s)



print(serialize(msg).encode())
print(msg.encode())

# a = ["a","b","c"]
# len(a)
# for index,s in enumerate(a):
#     print(index)
#     print(s)
#
# value=json.dumps(values)
# print(value)
#
# dictval = json.loads(value)
# print(dictval)
#
# value2=json.dumps(dictval)
# print(value2)
# r=requests.post(url,data=value,headers=headers)
# print(r.text)



