"""Utility classes and functions to work with the pipelines."""


import time
import datetime
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
            except (r.ReqlDriverError, r.ReqlOpFailedError) as exc:
                logger.exception(exc)
                time.sleep(1)


    def get_tx_in_backlog(self):
        # count = 0
        # logger.info('%s before update', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        start = time.time()*1000
        result = self.bigchain.update_assign_flag_limit(limit=5000)
        end = time.time()*1000
        if end-start>2000:
            print("update: start-",start,",end-",end,",cost-",end-start)
        if(len(result)):
            time.sleep(1)
        # logger.info('%s end update', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        if ('changes' in result) and len(result['changes'])>0:
            for tx in result['changes']:
                # count = count + 1
                # if count == 1:
                #     logger.info('%s in', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
                self.outqueue.put(tx['new_val'])
            # if count > 0:
            #     logger.info('%s :%s ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), count)



