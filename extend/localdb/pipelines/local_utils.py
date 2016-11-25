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

    def __init__(self, table, operation, prefeed=None):
        """Create a new RethinkDB ChangeFeed.

        Args:
            table (str): name of the table to listen to for changes.
            operation (int): can be ChangeFeed.INSERT, ChangeFeed.DELETE, or
                ChangeFeed.UPDATE. Combining multiple operation is possible using
                the bitwise ``|`` operator
                (e.g. ``ChangeFeed.INSERT | ChangeFeed.UPDATE``)
            prefeed (iterable): whatever set of data you want to be published
                first.
        """
        super().__init__(name='localchangefeed')
        self.prefeed = prefeed if prefeed else []
        self.table = table
        self.operation = operation
        self.bigchain = Bigchain()


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

            if is_insert and (self.operation & ChangeFeed.INSERT):
                self.outqueue.put(change['new_val'])
            elif is_delete and (self.operation & ChangeFeed.DELETE):
                self.outqueue.put(change['old_val'])
            elif is_update and (self.operation & ChangeFeed.UPDATE):
                self.outqueue.put(change['new_val'])