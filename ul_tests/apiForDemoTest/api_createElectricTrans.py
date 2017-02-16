import json
import requests

url='http://127.0.0.1:9984/uniledger/v1/block/queryByID/'
url='http://127.0.0.1:9984/uniledger/v1/timestat/txCreateAvgTime'
values = """{
    "block_id":"0163c975ef21cfdcd282f3dd9021800e7d2f17befc5f4a20aed91b22a04cb4e0",
}"""


headers = {
  'Content-Type': 'application/json'
}
value=json.dumps(values)
r=requests.post(url,data=value,headers=headers)
print(r.text)


# curl -i -X POST -H 'Content-Type:application/json' -d '{}' http://127.0.0.1:9984/uniledger/v1/block/queryByID//
