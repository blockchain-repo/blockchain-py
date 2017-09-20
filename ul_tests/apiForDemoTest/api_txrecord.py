import requests

pub = "9GxFx9CueGAm37qfEDEuhrkV4Dss4yF2FVgcKd9ZCSKf"
size = 10
num = 1
startTime = "1262275200000"
endTime = "4661462695"

url = 'http://localhost:9984/uniledger/v1/transaction/getTxRecord?' + \
      'public_key={}&pageSize={}&pageNum={}&startTime={}&endTime={}'.format(pub,
                                                                            size,
                                                                            num,
                                                                            "1505786776007",
                                                                            "fuck")
res = requests.get(url)
print(res.json())

url = 'http://localhost:9984/uniledger/v1/transaction/getTxRecord?' + \
      'public_key={}&pageSize={}&pageNum={}&startTime={}&endTime={}'.format(pub,
                                                                            size,
                                                                            num,
                                                                            "1262275200000",
                                                                            "1300000000000")
res = requests.get(url)
print(res.json())

url = 'http://localhost:9984/uniledger/v1/transaction/getTxRecord?' + \
      'public_key={}&pageSize={}&pageNum={}'.format(pub,
                                                    size,
                                                    num)
res = requests.get(url)
print(res.json())


# from bigchaindb import Bigchain
#
# b = Bigchain()
#
# print(b.gettxRecordByPubkey(pub, size, num, startTime, endTime))
