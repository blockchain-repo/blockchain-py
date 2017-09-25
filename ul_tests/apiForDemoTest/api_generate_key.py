import requests

url = 'http://localhost:9984/uniledger/v1/account/apiGenerateKeyPairs'
res = requests.get(url)
print(res.json())
