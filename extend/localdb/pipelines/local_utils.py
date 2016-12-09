"""Utility classes and functions to work with the pipelines for localdb."""

import time
import rethinkdb as r
import logging
from multipipes import Node
import bigchaindb
from bigchaindb import Bigchain

logger = logging.getLogger(__name__)


class ChangeFeed(Node):

    INSERT = 1
    DELETE = 2
    UPDATE = 4

    def __init__(self, table, table_class,operation,init_timestamp=0,round_recover_limit=None,
                 round_recover_limit_max=None,secondary_index=None ,prefeed=None):
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
        super().__init__(name='local_changefeed')
        self.prefeed = prefeed # current max timestamp data
        self.table = table
        self.table_class = table_class
        self.operation = operation
        self.bigchain = Bigchain()
        self.secondary_index = secondary_index

        # this round recovery timestamp start.
        self.init_timestamp = init_timestamp
        # this round recovery timestamp end, according to the changefeed set it,it will be the next round start
        # if should go on the next round deal!
        self.current_timestamp = None
        # this round the change data counts, if this round is zero, it will end up going on the round_recovery and
        # to the normal run_changefeed process.
        self.last_round_recovr_count = 0
        self.round_recover_count = 0
        self.nodes_count = len(bigchaindb.config['keyring']) + 1 # nodes count
        # this round will deal the max missing data, it will be dynamic change by the round_recovery process
        self.round_recover_limit_max = round_recover_limit_max if round_recover_limit_max else 1000
        self.round_recover_limit = self.round_recover_limit_max if round_recover_limit \
            and round_recover_limit >= self.round_recover_limit_max else round_recover_limit
        self.diff_time = 0 # adjacent data change deal cost time
        self.pre_round = 1 # prefeed deal round
        if table_class == 'vote':
            self.round_recover_limit *= self.nodes_count
            self.round_recover_limit_max *= self.nodes_count

    def run_forever(self):
        if self.prefeed:
            records_count,data = self.prefeed
            if records_count >= 1000000:
                self.round_recover_limit = 2000
                self.pre_round = records_count / 2000
            elif records_count >= 100000:
                self.pre_round = records_count / 2000
                self.round_recover_limit = 2000
            elif records_count >= 10000:
                self.pre_round = records_count / 1000
                self.round_recover_limit = 1000
            elif records_count >= 1000:
                self.pre_round = records_count / 1000
                self.round_recover_limit = 1000
            else:
                self.round_recover_limit = 1000

            while True:
                logger.info("{} has {} rounds to write the missing localdb data[count={}]"
                            .format(self.table_class, self.pre_round, records_count))
                self.round_write_localdb(data)
                self.pre_round -= 1
                if self.pre_round <= 0:
                    break

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

            if is_insert and (self.operation & ChangeFeed.INSERT):
                self.round_write_localdb(change['new_val'])
            elif is_delete and (self.operation & ChangeFeed.DELETE):
                # self.outqueue.put(change['old_val'])
                pass
            elif is_update and (self.operation & ChangeFeed.UPDATE):
                # self.outqueue.put(change['new_val'])
                pass

    def round_write_localdb(self,change_data):
        """send the change data to localdb pipelines

        Args:
            param change_data: changefeed data

        """

        self.diff_time = time.time()
        self.round_recover_count = 0  # each round set it to zero
        self.current_timestamp = change_data[self.table_class]['timestamp']

        # blur statics
        missing_data_count = self.bigchain.connection.run(
            r.table(self.table)
                .between(self.init_timestamp,
                         self.current_timestamp, left_bound='closed', right_bound='closed',
                         index=self.secondary_index)
                .order_by(index=r.asc(self.secondary_index)).count())

        round_recover_data = []

        if missing_data_count == 1:
            round_recover_data = [change_data]
        elif missing_data_count >= 2:
            if missing_data_count <= self.nodes_count:
                self.round_recover_limit = self.nodes_count * 2

            round_recover_data = self.bigchain.connection.run(
                r.table(self.table)
                    .between(self.init_timestamp,
                             self.current_timestamp, left_bound='closed', right_bound='closed',
                             index=self.secondary_index)
                    .order_by(index=r.asc(self.secondary_index)).limit(self.round_recover_limit))

        # logger.warning(
        #     "\nThis round the data to be put into {} [pipeline outqueue], interval number(fuzzy)={}, at most,
        #  {} records will be dealed in this round.\n".format(
        #         self.table_class, missing_data_count, self.round_recover_limit))

        last_data = None
        for data in round_recover_data:
            self.round_recover_count += 1
            self.outqueue.put(data)
            last_data = data
            # logger.warning(
            #     "\nASync recover data for {} has been put[pipeline outqueue], sequence number(fuzzy)={},
            # timestamp={}\n".format(self.table_class, self.round_recover_count, data[self.table_class]['timestamp']))

        # round init_timestamp must be set to the last missing_data timestamp for this round

        if last_data:
            self.init_timestamp = last_data[self.table_class]['timestamp']
            # print("Interval`s last data for {}, next round`s init_timestamp is {}\n".format(self.table_class,
            #                                                                                 self.init_timestamp))
            del last_data
        else:
            self.init_timestamp = self.current_timestamp
            # print("Interval has no data for {}, next round`s init_timestamp is {}\n".format(self.table_class,
            #                                                                                 self.init_timestamp))

        self.diff_time = time.time() - self.diff_time
        # logger.info("This round for {}[cost={}s,round_recover_count={},last_round_recovr_count={}]\n".format(
        #     self.table_class, self.diff_time, self.round_recover_count, self.last_round_recovr_count))

        # TODO: can be better
        # [closed,closed] 1+1=2 >=3
        if self.round_recover_count >= 3:
            if self.diff_time >= 90:
                self.round_recover_limit = int(self.round_recover_limit * 0.1) + 2
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

        if self.round_recover_limit >= self.round_recover_limit_max:
            self.round_recover_limit = self.round_recover_limit_max

        # logger.warning(
        #     "\nThis round the data have been put into {} [pipeline outqueue], interval number(fuzzy)={},
        # at most, {} records will be dealed in the next round.\n".format(
        #         self.table_class, missing_data_count, self.round_recover_limit))

        # record the round recover count
        self.last_round_recovr_count = self.round_recover_count
