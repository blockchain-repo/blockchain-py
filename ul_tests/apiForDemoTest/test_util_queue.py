"""Utility classes and functions to work with the pipelines."""


import time
import datetime
import rethinkdb as r
import logging
from multipipes import Node

from bigchaindb import Bigchain


logger = logging.getLogger(__name__)


class AddTxToQueue(Node):

    INSERT = 1
    DELETE = 2
    UPDATE = 4
    def __init__(self,operation=1, prefeed=None, bigchain=None):

        super().__init__(name='changefeed')
        self.prefeed = prefeed if prefeed else []
        self.operation = operation
        self.bigchain = bigchain or Bigchain()
        self.txStr={
    "id": "d875fbdadf6693d121b443cfa01a9a9256ae18e84bbc93dde8850881067d3e40" ,
    "transaction": {
        "asset": {
            "data": None ,
            "divisible": False ,
            "id": "ee9277a1-d8c7-41a3-86bc-8078ec9351ca" ,
            "refillable": False ,
            "updatable": False
        } ,
        "conditions": [
            {
                "amount": 1 ,
                "cid": 0 ,
                "condition": {
                    "details": {
                        "bitmask": 32 ,
                        "public_key": "5mVrPtqUzXwKYL2JeZo4cQq2spt8qfGVx3qE2V7NqgyU" ,
                        "signature": None ,
                        "type": "fulfillment" ,
                        "type_id": 4
                    } ,
                    "uri": "cc:4:20:RtTtCxNf1Bq7MFeIToEosMAa3v_jKtZUtqiWAXyFz1c:96"
                } ,
                "owners_after": [
                    "5mVrPtqUzXwKYL2JeZo4cQq2spt8qfGVx3qE2V7NqgyU"
                ]
            }
        ] ,
        "contracts": None ,
        "fulfillments": [
            {
                "fid": 0 ,
                "fulfillment": "cf:4:RtTtCxNf1Bq7MFeIToEosMAa3v_jKtZUtqiWAXyFz1d7uHEPYdeANttkdzF5sfzsOpPAa4HeQvZ9xPl61ObH1xJUOgm3Q93iVX7HRwzuz10GW0d3Ef1KCZ0bClBqugcI" ,
                "input": None ,
                "owners_before": [
                    "5mVrPtqUzXwKYL2JeZo4cQq2spt8qfGVx3qE2V7NqgyU"
                ]
            }
        ] ,
        "metadata": {
            "data": {
                "message": "Hello World from the BigchainDB"
            } ,
            "id": "8214065d-db18-4a44-a0ff-7b02bacb2785"
        } ,
        "operation": "GENESIS" ,
        "relaction": None ,
        "timestamp": "1504784119013"
    } ,
    "version": 1

}

    def run_forever(self):
        for element in self.prefeed:
            self.outqueue.put(element)
        self.get_tx_in_backlog()


    def get_tx_in_backlog(self):
        print("start in queue:",time.time()*1000)
        for i in range(5000):
            self.outqueue.put(self.txStr)
        print("end in queue:", time.time() * 1000)



