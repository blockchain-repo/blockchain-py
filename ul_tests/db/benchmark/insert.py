import time

import multiprocessing

from bigchaindb.core import Bigchain
from bigchaindb.common.crypto import generate_key_pair
from bigchaindb.common.transaction import Transaction, Asset


def transactions():
    priv, pub = generate_key_pair()
    tx = Transaction.create([pub], [([pub], 1)])
    while True:
        i = yield tx.to_dict()
        tx.asset = Asset(data={'n': i}, data_id='20170628150000', divisible=True)
        tx.sign([priv])


def write_tx():
    for a in range(times):
        txs = transactions()
        tx_list.append(txs.send(None))
    print("tx_list len", len(tx_list))
    b.backend.write_transaction(tx_list.pop())


b = Bigchain()
tx_list = []
times = 10000
num_clients = 30

start = time.time()
print("start", start)
for a in range(times):
    txs = transactions()
    tx_list.append(txs.send(None))
end = time.time()
print("end", end)
print("takes", end - start, "seconds")
print("create tx", times / (end - start), "times/s")


# for i in range(num_clients):
#     multiprocessing.Process(target=write_tx).start()

start2 = time.time()
print("start2", start2)
for a in tx_list:
    b.backend.write_transaction(a)
end2 = time.time()
print("end2", end2)
print("takes", end2 - start2, "seconds")
print("write tx", times / (end2 - start2), "times/s")
