from time import sleep
import json
import requests

from bigchaindb.common.util import gen_timestamp

delay = 3

with open('api_config') as fp:
    config = json.load(fp)

print("api config: ", config)
url = 'http://{}:{}/uniledger/v1/timestat/blockCreateAvgTimeByRange'.format(config['ip'], config['port'])

res = requests.post(url, json={'beginTime': "1487066476", 'endTime': gen_timestamp()})
print("api response:", res.json())
