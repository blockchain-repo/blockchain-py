import rapidjson
import requests
import time

from bigchaindb import config
# auto load lastest config
import bigchaindb.config_utils

from extend.localdb.restore.utils.common_utils import decode_data
from extend.localdb.restore.utils.leveldb_utils import LocaldbUtils

bigchaindb.config_utils.autoconfigure(force=True)

url_dict = dict()


restore_endpoint = config['restore_endpoint']
url_dict['node'] = '{}/collect/node/'.format(restore_endpoint)
url_dict['block'] = '{}/collect/block/'.format(restore_endpoint)
request_data = dict()

request_data['node'] = \
    {
        "status":"start",
        "target":"node",
        "desc":"collect node info"
    }

current_block_num = 1
request_data['block'] = \
    {
        "status": "start",
        "target": "block",
        "current_block_num": current_block_num,
        "desc": "collect node block_votes info"
    }

headers = {
  'Content-Type': "application/json"
}


def test_post(url, data):
    data = rapidjson.dumps(data)
    response = requests.post(url, data=data, headers=headers)
    result = None
    if response:
        code = response.status_code
        if code == 200:
            print("success request, param[url={},data={}]".format(url, data))
            result = response.content
            print(response.headers)
            compress = config['restore_server']['compress']
            result = decode_data(result,compress)
            print(result)
    else:
        print("timeout or error!")
    return result

if __name__ == "__main__":
    ldb = LocaldbUtils()
    free_conn = ldb.check_conn_free()
    if not free_conn:
        exit("localdb conn is busy, please check!")

    start = time.time()
    try:
        node_info = test_post(url_dict['node'],request_data['node'])
    except (BaseException,ConnectionRefusedError,ConnectionError) as msg:
        exit(msg)

    block_num = node_info['block_num']
    type = 'block'
    data = None
    url = None
    if type == 'node':
        url = url_dict[type]
        data = request_data[type]
    elif type == 'block':
        url = url_dict[type]
        data = request_data[type]
        for i in range(1,block_num+1):
            data['current_block_num'] = i
            test_post(url,data=data)
    else:
        exit(0,'error request')
    cost = time.time() - start
    print("cost time {}s".format(cost))

