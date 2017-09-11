"""Utility classes and functions to work with the pipelines."""


import time
import datetime
import rethinkdb as r
import logging
from multipipes import Node
import multiprocessing as mp
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
            except (r.ReqlDriverError, r.ReqlOpFailedError) as exc:
                logger.exception(exc)
                time.sleep(1)


    def get_tx_in_backlog(self):
        pool = mp.Pool(processes=int(15))
        result = pool.map(get_batch_txs, range(15))
        for i in range(len(result)):
            if ('changes' in result[i]) and len(result[i]['changes']) > 0:
                for tx in result[i]['changes']:
                    self.outqueue.put(tx['new_val'])
        pool.close()
        pool.join()

def get_batch_txs(num):
    start = 500 * num
    end = 500 * (num+1)
    # start_time = time.time() * 1000
    bigchain = Bigchain()
    result = bigchain.update_assign_flag_limit(start=start,end=end)
    # end_time = time.time() * 1000
    # if 'changes' in result:
    #     print('len::',len(result['changes']),",update: start-", start_time, ",end-", end_time, ",cost-", end_time - start_time)
    if (len(result)):
        time.sleep(1)
    return result