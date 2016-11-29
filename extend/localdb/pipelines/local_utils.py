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

    def __init__(self, table, table_class,operation,init_timestamp=0,repeat_recover_round=None,secondary_index=None ,prefeed=None):
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
        self.first_changes = True

        # this round recovery timestamp start
        self.init_timestamp = init_timestamp
        # this round recovery timestamp end, according to the changefeed set it,it will be the next round start
        # if should go on the next round deal!
        self.current_timestamp = None
        # this round the change data counts, if this round is zero, it will end up going on the round_recovery and
        # to the normal run_changefeed process
        self.round_recover_count = 0
        # if go on recovery the lost data
        self.round_recovery = True
        # make sure the data can be recover mostly or even fully, should run round recovery more than one times
        self.repeat_recover_round = repeat_recover_round or 5


    def run_forever(self):

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

            if self.round_recovery:
                self.round_recover_count = 0 # each round set it to zero
                self.current_timestamp = change['new_val'][self.table_class]['timestamp']
                missing_data = self.bigchain.connection.run(
                    r.table(self.table)
                        .between(self.init_timestamp,
                                 self.current_timestamp, left_bound='open', right_bound='closed',
                                 index=self.secondary_index)
                        .order_by(index=r.asc(self.secondary_index)))
                # print('miss data {}'.format(missing_data))
                # print('miss data size={}'.format(len(missing_data)))

                for data in missing_data:
                    self.round_recover_count = self.round_recover_count + 1
                    self.outqueue.put(data)
                    logger.warning(
                        "\nRecover data for {}, number={}, timestamp={}".format(
                            self.table_class, self.round_recover_count, data[self.table_class]['timestamp']))

                if self.round_recover_count == 1 or self.round_recover_count == 0:
                    self.repeat_recover_round = self.repeat_recover_round - 1
                    logger.warning("\nThis round recover data for {}, count is {} (in [0,1]), will exit the round_recovery dealing after {} rounds!\n"\
                                   .format(self.table_class,self.round_recover_count,self.repeat_recover_round ))
                else:
                    self.repeat_recover_round = self.repeat_recover_round + 1
                    logger.warning(
                        "\nThis round recover data for {}, count is {} (> 1), will increase the round_recovery dealing rounds to {}!\n" \
                        .format(self.table_class,self.round_recover_count, self.repeat_recover_round))

                self.init_timestamp = self.current_timestamp

                if self.repeat_recover_round <= 0:
                    self.round_recovery = False
                    logger.warning(
                        "\n{}`s all round recovery are so OK and it will exit the recovery process and go into normal changefeed dealinig!\n" \
                        .format(self.table_class,self.repeat_recover_round, self.repeat_recover_round))

            else:
                if is_insert and (self.operation & ChangeFeed.INSERT):
                    self.outqueue.put(change['new_val'])
                elif is_delete and (self.operation & ChangeFeed.DELETE):
                    self.outqueue.put(change['old_val'])
                elif is_update and (self.operation & ChangeFeed.UPDATE):
                    self.outqueue.put(change['new_val'])
