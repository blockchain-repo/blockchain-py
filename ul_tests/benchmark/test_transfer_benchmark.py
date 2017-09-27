import json
import time
from queue import Full

import requests
import multiprocessing
from collections import namedtuple
from cryptoconditions import crypto

from bigchaindb.common.transaction import Transaction, Asset, Fulfillment
from bigchaindb.common.util import gen_timestamp

CryptoKeypair = namedtuple('CryptoKeypair', ('private_key', 'public_key'))

delay = 10  # block,vote
num_clients = 10
count = 100
create_queue = multiprocessing.Queue(maxsize=count)
transfer_queue = multiprocessing.Queue(maxsize=count)


def generate_keypair():
    return CryptoKeypair(
        *(k.decode() for k in crypto.ed25519_generate_key_pair()))


def create_transfer(p_num):
    while True:
        alice, bob = generate_keypair(), generate_keypair()

        asset = Asset(data={'money': 'RMB'}, data_id='20170628150000', divisible=True)
        metadata = {'planet': 'earth'}
        tx_create = Transaction.create([alice.public_key], [([alice.public_key], 1)], metadata=metadata, asset=asset)
        tx_create = tx_create.sign([alice.private_key])
        try:
            create_queue.put_nowait(tx_create)
        except Full:
            print(p_num, ":create_queue full")
            break

        cid = 0
        condition = tx_create.to_dict()['transaction']['conditions'][cid]
        inputs = Fulfillment.from_dict({
            'fulfillment': condition['condition']['details'],
            'input': {
                'cid': cid,
                'txid': tx_create.to_dict()['id'],
            },
            'owners_before': condition['owners_after'],
        })
        asset = Asset.from_dict(tx_create.to_dict()['transaction']['asset'])
        tx_transfer = Transaction.transfer([inputs], [([bob.public_key], 1)], asset)
        tx_transfer = tx_transfer.sign([alice.private_key])
        try:
            transfer_queue.put_nowait(tx_transfer)
        except Full:
            print(p_num, "transfer_queue full")
            break


def post_create():
    while True:
        headers = {'content-type': 'application/json'}
        url = 'http://localhost:9984/uniledger/v1/transaction/createOrTransferTx'
        value = json.dumps(create_queue.get().to_dict())
        requests.post(url, data=value, headers=headers)


def post_transfer():
    while True:
        headers = {'content-type': 'application/json'}
        url = 'http://localhost:9984/uniledger/v1/transaction/createOrTransferTx'
        value = json.dumps(transfer_queue.get().to_dict())
        requests.post(url, data=value, headers=headers)


if __name__ == '__main__':
    # create_queue and transfer_queue
    for x in range(num_clients):
        p = multiprocessing.Process(target=create_transfer, args=(x,))
        p.start()

    # wait for full
    while True:
        if transfer_queue.qsize() == count:
            break
        time.sleep(delay)
        print("transfer qsize:", transfer_queue.qsize())

    # post create
    for x in range(num_clients):
        p = multiprocessing.Process(target=post_create)
        p.start()

    # wait for post create
    while True:
        if create_queue.empty():
            break
        time.sleep(1)
        print("create qsize:", create_queue.qsize())

    time.sleep(10)

    ################
    # ready, go!
    ################

    # post transfer
    transfer_start = gen_timestamp()
    for x in range(num_clients):
        p = multiprocessing.Process(target=post_transfer)
        p.start()

    # wait for post transfer
    while True:
        if transfer_queue.empty():
            break
        time.sleep(1)
        print("transfer qsize:", transfer_queue.qsize())
    transfer_end = gen_timestamp()
    transfer_cost = (int(transfer_end) - int(transfer_start)) / 1000
    print("transfer_start:", transfer_start)
    print("transfer_end:", transfer_end)
    print("transfer_cost:", transfer_cost)
