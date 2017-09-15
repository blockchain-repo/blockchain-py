import requests

pub = "9GxFx9CueGAm37qfEDEuhrkV4Dss4yF2FVgcKd9ZCSKf"
size = 1
num = 1
url = 'http://localhost:9984/uniledger/v1/transaction/getTxRecord?public_key={}&pageSize={}&pageNum={}'.format(pub,
                                                                                                               size,
                                                                                                               num)
res = requests.get(url)
print(res.json())
