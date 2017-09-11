import requests
import time

from bigchaindb.common.transaction import Transaction, Asset, Fulfillment
from bigchaindb.common.crypto import generate_key_pair


pri_m1, pub_m1 = generate_key_pair()
pri_m2, pub_m2 = generate_key_pair()
pri_n1, pub_n1 = generate_key_pair()
pri_n2, pub_n2 = generate_key_pair()
pri_n3, pub_n3 = generate_key_pair()

delay = 4
msg = "m_to_n"
asset = Asset(data={'money': 'RMB'}, data_id='20170628150000', divisible=True)
metadata = {'raw': msg}
amount_m1 = 6000
amount_m2 = 4000
amount_n1 = 2000
amount_n2 = 3000
amount_n3 = 5000

tx_m1 = Transaction.create([pub_m1], [([pub_m1], amount_m1)], metadata=metadata, asset=asset)
tx_m1 = tx_m1.sign([pri_m1]).to_dict()

tx_m2 = Transaction.create([pub_m2], [([pub_m2], amount_m2)], metadata=metadata, asset=asset)
tx_m2 = tx_m2.sign([pri_m2]).to_dict()
print("========create tx======")
with requests.Session() as session:
    res = session.post('http://localhost:9984/uniledger/v1/transaction/createOrTransferTx', json=tx_m1)
    print(res.json())
    assert res.status_code == 202
    res = session.post('http://localhost:9984/uniledger/v1/transaction/createOrTransferTx', json=tx_m2)
    print(res.json())
    assert res.status_code == 202
print("========wait for block and vote...========")
time.sleep(delay)
inputs = []
with requests.Session() as session:
    res = session.get(
        'http://localhost:9984/uniledger/v1/condition/getUnspentTxs?unspent=true&public_key={}'.format(pub_m1))
    assert res.status_code == 200
    balance = 0
    for i in res.json()['data']:
        f = Fulfillment.from_dict({
            'fulfillment': i['details'],
            'input': {
                'cid': i['cid'],
                'txid': i['txid'],
            },
            'owners_before': [pub_m1],
        })
        inputs.append(f)
        balance += i['amount']
    print("========pub_m1 balance======\n", balance)
    print(res.json())

    res = session.get(
        'http://localhost:9984/uniledger/v1/condition/getUnspentTxs?unspent=true&public_key={}'.format(pub_m2))
    assert res.status_code == 200
    balance = 0
    for i in res.json()['data']:
        f = Fulfillment.from_dict({
            'fulfillment': i['details'],
            'input': {
                'cid': i['cid'],
                'txid': i['txid'],
            },
            'owners_before': [pub_m2],
        })
        inputs.append(f)
        balance += i['amount']
    print("========pub_m2 balance======\n", balance)
    print(res.json())
print("========m1,m2 transfer to pub_n1,pub_n2,pub_n3======")
tx = Transaction.transfer(inputs, [([pub_n1], amount_n1), ([pub_n2], amount_n2), ([pub_n3], amount_n3)], asset,
                          metadata)
tx = tx.sign([pri_m1, pri_m2]).to_dict()
with requests.Session() as session:
    res = session.post('http://localhost:9984/uniledger/v1/transaction/createOrTransferTx', json=tx)
    print(res.json())
    assert res.status_code == 202
print("========wait for block and vote...========")
time.sleep(delay)
with requests.Session() as session:
    res = session.get(
        'http://localhost:9984/uniledger/v1/condition/getUnspentTxs?unspent=true&public_key={}'.format(pub_m1))
    assert res.status_code == 200
    balance = 0
    for i in res.json()['data']:
        balance += i['amount']
    print("========pub_m1 balance======\n", balance)
    print(res.json())
with requests.Session() as session:
    res = session.get(
        'http://localhost:9984/uniledger/v1/condition/getUnspentTxs?unspent=true&public_key={}'.format(pub_m2))
    assert res.status_code == 200
    balance = 0
    for i in res.json()['data']:
        balance += i['amount']
    print("========pub_m1 balance======\n", balance)
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
