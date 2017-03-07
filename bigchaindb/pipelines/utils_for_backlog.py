"""Utility classes and functions to work with the pipelines."""


import time
import rethinkdb as r
import logging
from multipipes import Node

from bigchaindb import Bigchain


logger = logging.getLogger(__name__)


class BacklogTxToQueue(Node):

    INSERT = 1
    DELETE = 2
    UPDATE = 4

    def __init__(self,operation=1, prefeed=None, bigchain=None):

        super().__init__(name='changefeed')
        self.prefeed = prefeed if prefeed else []
        self.operation = operation
        self.bigchain = bigchain or Bigchain()

    def run_forever(self):
        for element in self.prefeed:
            self.outqueue.put(element)

        while True:
            try:
                self.get_tx_in_backlog()
                #TODO no data
                # print('utiles run forever done ,now break!!???')
            except (r.ReqlDriverError, r.ReqlOpFailedError) as exc:
                logger.exception(exc)
                time.sleep(1)


    def get_tx_in_backlog(self):
        for tx in self.bigchain.get_tx_from_backlog():
            self.outqueue.put(tx)
            self.bigchain.update_assign_is_deal(tx['id'])


