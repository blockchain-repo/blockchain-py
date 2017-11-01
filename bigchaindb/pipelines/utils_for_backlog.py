"""Utility classes and functions to work with the pipelines."""

import time
import datetime
import rethinkdb as r
import logging
from multipipes import Node
import multiprocessing as mp
from bigchaindb import Bigchain, config

logger = logging.getLogger(__name__)


class BacklogTxToQueue(Node):
    INSERT = 1
    DELETE = 2
    UPDATE = 4

    def __init__(self, operation=1, prefeed=None, bigchain=None):

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
        processes_num = config['argument_config']['block_pipeline.get_txs_processes_num']
        pool = mp.Pool(processes=int(processes_num))
        result = pool.map(get_batch_txs, range(processes_num))
        for i in range(len(result)):
            if ('changes' in result[i]) and len(result[i]['changes']) > 0:
                for tx in result[i]['changes']:
                    self.outqueue.put(tx['new_val'])
        pool.close()
        pool.join()


def get_batch_txs(num):
    get_txs_everytime = config['argument_config']['block_pipeline.get_txs_everytime']
    start = get_txs_everytime * num
    end = get_txs_everytime * (num + 1)
    start_time = time.time() * 1000
    bigchain = Bigchain()
    result = bigchain.update_assign_flag_limit(start=start, end=end)
    end_time = time.time() * 1000
    if 'changes' in result:
        logger.debug('len::%d, update: start-%d ,end-%d ,cost-%d', len(result['changes']), start_time, end_time,
                     end_time - start_time)
    if len(result):
        time.sleep(1)
    return result
