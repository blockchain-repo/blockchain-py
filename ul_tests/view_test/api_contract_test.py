import requests

url0 = 'http://0.0.0.0:9984/uniledger/v1/transaction/createByPayload/'
url1 = 'http://127.0.0.1:9984/uniledger/v1/contract/createContract/'
url2 = 'http://127.0.0.1:9984/uniledger/v1/contract/createContractTx'
url3 = 'http://127.0.0.1:9984/uniledger/v1/contract/getContract'
url4 = 'http://127.0.0.1:9984/uniledger/v1/contract/getContractTx'
url5 = 'http://127.0.0.1:9984/uniledger/v1/contract/getContractRecord'
url6 = 'http://127.0.0.1:9984/uniledger/v1/contract/freezeAsset'
url7 = 'http://127.0.0.1:9984/uniledger/v1/contract/unfreezeAsset'
url8 = 'http://127.0.0.1:9984/uniledger/v1/contract/frozenAsset'
url9 = 'http://127.0.0.1:9984/uniledger/v1/contract/getCanSpend'
url10 = 'http://127.0.0.1:9984/uniledger/v1/contract/getUnSpend'

headers = {'content-type': 'application/json'}
data1 = {}

ret = requests.post(url1,data=data1,headers=headers)
# ret = requests.get(url3,data=data1,headers=headers)
print(ret)

