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

    def __init__(self, table, table_class,operation,init_timestamp=0,repeat_recover_round=None,
                 round_recover_limit=None,secondary_index=None ,prefeed=None):
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

        # this round recovery timestamp start.
        self.init_timestamp = init_timestamp
        # this round recovery timestamp end, according to the changefeed set it,it will be the next round start
        # if should go on the next round deal!
        self.current_timestamp = None
        # this round the change data counts, if this round is zero, it will end up going on the round_recovery and
        # to the normal run_changefeed process.
        self.round_recover_count = 0
        # if go on recovery the lost data
        self.round_recovery = True
        # make sure the data can be recover mostly or even fully, should run round recovery process more than one times
        # it will be dynamic change by the round_recovery process
        self.repeat_recover_round = repeat_recover_round or 10
        # this round will deal the max missing data, it will be dynamic change by the round_recovery process
        self.round_recover_limit = round_recover_limit or 100
        self.read_delay_time = 1 # the interval time for read the rethinkdb`data by timestamp, must >=1 s
        self.diff_time = 0 # adjacent data change cost time


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
                self.diff_time = time.time()
                self.round_recover_count = 0 # each round set it to zero
                self.current_timestamp = change['new_val'][self.table_class]['timestamp']

                # must set the delay for read the data, avoid the loss at the same time read and write!
                # read_delay_time = 1s
                time.sleep(self.read_delay_time)

                missing_data_count = self.bigchain.connection.run(
                    r.table(self.table)
                        .between(self.init_timestamp,
                                 self.current_timestamp, left_bound='open', right_bound='closed',
                                 index=self.secondary_index)
                        .order_by(index=r.asc(self.secondary_index)).count())

                logger.warning(
                    "\nThe total data to be put into {} [pipeline outqueue], total numbers={}, the max number will be {} in this round.\n".format(
                        self.table_class,missing_data_count, self.round_recover_limit))

                # the data ,this round will recover
                round_recover_data = []
                if missing_data_count == 1:
                    # must be wrap to the list
                    round_recover_data = [change['new_val']]

                elif missing_data_count >= 2:
                    if missing_data_count <= self.round_recover_limit:
                        self.round_recover_limit = missing_data_count

                    round_recover_data = self.bigchain.connection.run(
                        r.table(self.table)
                            .between(self.init_timestamp,
                                     self.current_timestamp, left_bound='open', right_bound='closed',
                                     index=self.secondary_index)
                            .order_by(index=r.asc(self.secondary_index)).limit(self.round_recover_limit))

                # print('miss data {}'.format(missing_data))
                # print('miss data size={}'.format(len(missing_data)))
                for data in round_recover_data:
                    self.round_recover_count = self.round_recover_count + 1
                    self.outqueue.put(data)
                    logger.warning(
                        "\nASync recover data for {}, number={}, timestamp={}\n".format(
                            self.table_class, self.round_recover_count, data[self.table_class]['timestamp']))

                # round init_timestamp must be set to the last missing_data timestamp for this round
                if data:
                    self.init_timestamp = data[self.table_class]['timestamp']
                    print("last data for {}, init_timestamp is {}\n".format(self.table_class,self.init_timestamp))
                else:
                    self.init_timestamp = self.current_timestamp
                    print("no data for {}, current_timestamp is {}\n".format(self.table_class, self.init_timestamp))

                if self.round_recover_count == 1 or self.round_recover_count == 0:
                    self.repeat_recover_round = self.repeat_recover_round - 1
                    logger.warning("\nThis round puts the data into {} [pipeline outqueue], count is {} (in [0,1]), will exit the round_recovery dealing after {} rounds!\n" \
                                   .format(self.table_class,self.round_recover_count,self.repeat_recover_round ))
                else:
                    self.repeat_recover_round = self.repeat_recover_round + 1
                    logger.warning(
                        "\nThis round puts the data into {} [pipeline outqueue], count is {} (> 1), will increase the round_recovery dealing rounds to {}!\n" \
                            .format(self.table_class,self.round_recover_count, self.repeat_recover_round))

                if self.repeat_recover_round <= 0:
                    self.round_recovery = False
                    logger.warning(
                        "\n{}`s all round recovery are so OK and it will exit the round recovery process and go into normal changefeed dealinig!\n" \
                            .format(self.table_class,self.repeat_recover_round, self.repeat_recover_round))

                self.diff_time = time.time() - self.diff_time
                print("cost time {}".format(self.diff_time))

                # TODO: can be better
                if self.round_recover_count >= 2:
                    if self.diff_time >= 90:
                        self.round_recover_limit = int(self.round_recover_limit*0.1) + 2
                    elif self.diff_time >= 60:
                        self.round_recover_limit = int(self.round_recover_limit * 0.3) + 2
                    elif self.diff_time >= 30:
                        self.round_recover_limit = int(self.round_recover_limit * 0.4) + 2
                    elif self.diff_time >= 10:
                        self.round_recover_limit = int(self.round_recover_limit * 0.5) + 2
                    elif self.diff_time >= 5:
                        self.round_recover_limit = int(self.round_recover_limit * 0.6) + 2
                    elif self.diff_time >= 2:
                        self.round_recover_limit = int(self.round_recover_limit * 0.8) + 2
                    elif self.diff_time >= 1:
                        self.round_recover_limit = int(self.round_recover_limit * 1.5) + 2
                    elif self.diff_time >= 0.1:
                        self.round_recover_limit = int(self.round_recover_limit * 2.0) + 2
                    elif self.diff_time >= 0.01:
                        self.round_recover_limit = int(self.round_recover_limit * 2.5) + 2
                    else:
                        self.round_recover_limit = int(self.round_recover_limit * 4) + 2

                logger.warning(
                    "\nThe total data to be put into {} [pipeline outqueue], total numbers={}, the max number will be {} in next round.\n".format(
                        self.table_class, missing_data_count, self.round_recover_limit))
            else:
                if is_insert and (self.operation & ChangeFeed.INSERT):
                    self.outqueue.put(change['new_val'])
                elif is_delete and (self.operation & ChangeFeed.DELETE):
                    self.outqueue.put(change['old_val'])
                elif is_update and (self.operation & ChangeFeed.UPDATE):
                    self.outqueue.put(change['new_val'])
