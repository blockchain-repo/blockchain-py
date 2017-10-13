import json
import time
from queue import Full, Empty

import requests
import multiprocessing
from collections import namedtuple
from cryptoconditions import crypto

from bigchaindb.common.transaction import Transaction, Asset, Fulfillment
from bigchaindb.common.util import gen_timestamp

CryptoKeypair = namedtuple('CryptoKeypair', ('private_key', 'public_key'))

host = "localhost"
port = "9984"
db_port = "28015"

num_clients = 10
count = 1000
create_queue = multiprocessing.Queue(maxsize=count)
transfer_queue = multiprocessing.Queue(maxsize=count)


def generate_keypair():
    return CryptoKeypair(
        *(k.decode() for k in crypto.ed25519_generate_key_pair()))


def create_transfer(p_num):
    print(p_num, ":create_transfer start")
    while True:
        alice, bob = generate_keypair(), generate_keypair()

        asset = Asset(data={'money': 'RMB'}, data_id='20170628150000', divisible=True)
        metadata = {'planet': 'earth'}
        tx_create = Transaction.create([alice.public_key], [([alice.public_key], 1)], metadata=metadata, asset=asset)
        tx_create = tx_create.sign([alice.private_key])
        try:
            create_queue.put(tx_create, False)
        except Full:
            print(p_num, ":create_queue full", create_queue.qsize())
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
            transfer_queue.put(tx_transfer, False)
        except Full:
            print(p_num, ":transfer_queue full")
            break


def post_create(p_num):
    while True:
        headers = {'content-type': 'application/json'}
        url = 'http://{}:{}/uniledger/v1/transaction/createOrTransferTx'.format(host, port)
        try:
            value = create_queue.get(False)
        except Empty:
            if create_queue.qsize() > 0:
                # print(p_num, ":create_queue not actually empty", create_queue.qsize())
                continue
            print(p_num, ":create_queue empty", create_queue.qsize())
            break
        value = json.dumps(value.to_dict())
        requests.post(url, data=value, headers=headers)


def post_transfer(p_num):
    while True:
        headers = {'content-type': 'application/json'}
        url = 'http://{}:{}/uniledger/v1/transaction/createOrTransferTx'.format(host, port)
        try:
            value = transfer_queue.get(False)
        except Empty:
            if transfer_queue.qsize() > 0:
                # print(p_num, ":transfer_queue not actually empty", transfer_queue.qsize())
                continue
            print(p_num, ":transfer_queue empty", transfer_queue.qsize())
            break
        value = json.dumps(value.to_dict())
        requests.post(url, data=value, headers=headers)


if __name__ == '__main__':
    # create_queue and transfer_queue
    print("step 1 :generate kaypair, create tx(create_queue), transfer(transfer_queue)")
    for x in range(num_clients):
        p = multiprocessing.Process(target=create_transfer, args=(x,))
        p.start()

    # wait for 'Full'
    while True:
        if transfer_queue.full():
            break
        time.sleep(1)
        print("m :transfer qsize:", transfer_queue.qsize())

    input("Press enter key to continue...")

    # post create
    print("step 2 :post create tx ,please wait for all create tx valid")
    for x in range(num_clients):
        p = multiprocessing.Process(target=post_create, args=(x,))
        p.start()

    # wait for post create
    while True:
        if create_queue.empty():
            break
        time.sleep(1)
        print("m :create qsize:", create_queue.qsize())

    #
    input("Press enter key to continue...")

    BANNER = """
    *******************
    *   ready, go!    *
    *******************
    """
    print(BANNER)

    # post transfer
    print("step 3 :post transfer tx ,please wait for all transfer tx valid")
    transfer_start = gen_timestamp()
    for x in range(num_clients):
        p = multiprocessing.Process(target=post_transfer, args=(x,))
        p.start()

    # wait for post transfer
    while True:
        if transfer_queue.empty():
            break
        time.sleep(1)
        print("m :transfer qsize:", transfer_queue.qsize())
    transfer_end = gen_timestamp()
    transfer_cost = (int(transfer_end) - int(transfer_start)) / 1000
    print("m :transfer_start:", transfer_start)
    print("m :transfer_end:", transfer_end)
    print("m :transfer_cost:", transfer_cost)
