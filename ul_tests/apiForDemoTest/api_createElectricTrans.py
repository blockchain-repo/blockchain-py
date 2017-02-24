import json
import requests

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
# url='http://127.0.0.1:9984/uniledger/v1/transaction/createByUser/'
# values = {
#                 "payload":"test"
#             }

url='http://127.0.0.1:9984/uniledger/v1/transaction/getTxRecord?public_key={}'.format('Gvexu49oskc6ptYwzqP9q8sL9jLxjNZNMBWgVVhUtPmD')



r=requests.get(url)

print(r.text)




headers = {
  'Content-Type': 'application/json'
}
# value=json.dumps(values)
# r=requests.post(url,data=value,headers=headers)
# print(r.text)



