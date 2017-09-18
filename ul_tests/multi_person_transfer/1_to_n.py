import requests
import time

from bigchaindb.common.transaction import Transaction, Asset, Fulfillment
from bigchaindb.common.crypto import generate_key_pair

# 一对多转账，生成1+3个公钥
pri_1, pub_1 = generate_key_pair()
pri_n1, pub_n1 = generate_key_pair()
pri_n2, pub_n2 = generate_key_pair()
pri_n3, pub_n3 = generate_key_pair()

delay = 4  # 发送交易后，等待建块投票延迟
msg = "1_to_n"
asset = Asset(data={'money': 'RMB'}, data_id='20170628150000', divisible=True)
metadata = {'raw': msg}

# pub_1先创建10000，再转给n1，n2，n3各2000/3000/5000
amount = 10000
amount_n1 = 2000
amount_n2 = 3000
amount_n3 = 5000

# pub_1创建交易
tx = Transaction.create([pub_1], [([pub_1], amount)], metadata=metadata, asset=asset)
tx = tx.sign([pri_1]).to_dict()
print("========create tx======")

# 发送给区块链节点
with requests.Session() as session:
    res = session.post('http://localhost:9984/uniledger/v1/transaction/createOrTransferTx', json=tx)
    print(res.json())
    assert res.status_code == 202
print("========wait for block and vote...========")
time.sleep(delay)

# 获取utxo，计算余额
inputs = []
with requests.Session() as session:
    res = session.get(
        'http://localhost:9984/uniledger/v1/condition/getUnspentTxs?unspent=true&public_key={}'.format(pub_1))
    assert res.status_code == 200
    balance = 0
    for i in res.json()['data']:
        f = Fulfillment.from_dict({
            'fulfillment': i['details'],
            'input': {
                'cid': i['cid'],
                'txid': i['txid'],
            },
            'owners_before': [pub_1],
        })
        inputs.append(f)
        balance += i['amount']
    print("========pub_1 balance======\n", balance)
    print(res.json())

# 转移资产交易pub_1->n1,n2,n3
print("========transfer to pub_n1,pub_n2,pub_n3======")
tx = Transaction.transfer(inputs, [([pub_n1], amount_n1), ([pub_n2], amount_n2), ([pub_n3], amount_n3)], asset,
                          metadata)
tx = tx.sign([pri_1]).to_dict()

# 发送给区块链节点
with requests.Session() as session:
    res = session.post('http://localhost:9984/uniledger/v1/transaction/createOrTransferTx', json=tx)
    print(res.json())
    assert res.status_code == 202
print("========wait for block and vote...========")
time.sleep(delay)

# pub_1,n1,n2,n3各自获取utxo，计算余额
with requests.Session() as session:
    res = session.get(
        'http://localhost:9984/uniledger/v1/condition/getUnspentTxs?unspent=true&public_key={}'.format(pub_1))
    assert res.status_code == 200
    balance = 0
    for i in res.json()['data']:
        balance += i['amount']
    print("========pub_1 balance======\n", balance)
    print(res.json())

with requests.Session() as session:
    res = session.get(
        'http://localhost:9984/uniledger/v1/condition/getUnspentTxs?unspent=true&public_key={}'.format(pub_n1))
    assert res.status_code == 200
    balance = 0
    for i in res.json()['data']:
        balance += i['amount']
    print("========pub_n1 balance======\n", balance)
    print(res.json())
with requests.Session() as session:
    res = session.get(
        'http://localhost:9984/uniledger/v1/condition/getUnspentTxs?unspent=true&public_key={}'.format(pub_n2))
    assert res.status_code == 200
    balance = 0
    for i in res.json()['data']:
        balance += i['amount']
    print("========pub_n2 balance======\n", balance)
    print(res.json())
with requests.Session() as session:
    res = session.get(
        'http://localhost:9984/uniledger/v1/condition/getUnspentTxs?unspent=true&public_key={}'.format(pub_n3))
    assert res.status_code == 200
    balance = 0
    for i in res.json()['data']:
        balance += i['amount']
    print("========pub_n3 balance======\n", balance)
    print(res.json())
