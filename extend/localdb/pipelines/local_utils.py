"""Utility classes and functions to work with the pipelines for localdb."""

import time
import rethinkdb as r
import logging
from multipipes import Node

from bigchaindb import Bigchain

logger = logging.getLogger(__name__)


class ChangeFeed(Node):

    INSERT = 1
    DELETE = 2
    UPDATE = 4

    def __init__(self, table, table_class,operation,init_timestamp=0,secondary_index=None ,prefeed=None):
        """Create a new RethinkDB ChangeFeed.

        Args:
            table (str): name of the table to listen to for changes.
            operation (int): can be ChangeFeed.INSERT, ChangeFeed.DELETE, or
                ChangeFeed.UPDATE. Combining multiple operation is possible using
                the bitwise ``|`` operator
                (e.g. ``ChangeFeed.INSERT | ChangeFeed.UPDATE``)
            secondary_index (str): name of the table secondary_index for fixing the miss changefeed data
            prefeed (iterable): whatever set of data you want to be published
                first.
        """
        super().__init__(name='localchangefeed')
        self.prefeed = prefeed if prefeed else []
        self.table = table
        self.table_class = table_class
        self.operation = operation
        self.bigchain = Bigchain()
        self.secondary_index = secondary_index
        self.init_timestamp = init_timestamp
        self.current_timestamp = None
        self.first_changes = True
        self.missing_count = 0


    def run_forever(self):
        # time.sleep(20)
        # logger.error('{} start'.format(self.table))

        for element in self.prefeed:
            self.outqueue.put(element)

        while True:
            try:
                self.run_changefeed()
                break
            except (r.ReqlDriverError, r.ReqlOpFailedError) as exc:
                logger.exception(exc)
                time.sleep(1)



    def run_changefeed(self):
        for change in self.bigchain.connection.run(r.table(self.table).changes()):
            is_insert = change['old_val'] is None
            is_delete = change['new_val'] is None
            is_update = not is_insert and not is_delete

            if self.first_changes:
                self.current_timestamp = change['new_val'][self.table_class]['timestamp']
                self.first_changes = False
                bigchain = Bigchain()
                # print('run_forever4')
                # print(change['new_val'])
                # print("type of2 is {}".format(type(change['new_val'])))
                missing_data = bigchain.connection.run(
                    r.table(self.table)
                        .between(self.init_timestamp,
                                 # self.current_timestamp, left_bound='open',
                                 self.current_timestamp,left_bound='open', right_bound='open',
                                 index=self.secondary_index)
                        .order_by(index=r.asc(self.secondary_index)))
                # print('miss data {}'.format(missing_data))
                # print('miss data size={}'.format(len(missing_data)))
                for data in missing_data:
                    self.missing_count = self.missing_count + 1
                    logger.warning(
                        "\nmissing data for {},number={},timestamp={}".format(
                            self.table_class, self.missing_count, data[self.table_class]['timestamp']))
                    # print("type of is {}".format(type(data)))
                    self.outqueue.put(data)
                self.init_timestamp = None
                self.first_changes = False

            if is_insert and (self.operation & ChangeFeed.INSERT):
                self.outqueue.put(change['new_val'])
            elif is_delete and (self.operation & ChangeFeed.DELETE):
                self.outqueue.put(change['old_val'])
            elif is_update and (self.operation & ChangeFeed.UPDATE):
                self.outqueue.put(change['new_val'])
