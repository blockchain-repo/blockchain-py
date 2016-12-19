
import time
import logging

import bigchaindb
import rethinkdb as r
import bigchaindb.config_utils
from bigchaindb import config_utils
from extend.localdb.restore.rethinkdb_utils import utils as rethinkdb_utils
from bigchaindb.common.exceptions import *

logger = logging.getLogger(__name__)


class RethinkdbUtils():

    def __init__(self, host=None, port=None, dbname=None, backend=None):
        config_utils.autoconfigure()
        self.host = host or bigchaindb.config['database']['host']
        self.port = port or bigchaindb.config['database']['port']
        self.dbname = "restore_{}".format(dbname or bigchaindb.config['database']['name'])
        self.backend = backend or rethinkdb_utils.get_backend(host, port, dbname)
        self.connection = rethinkdb_utils.Connection(host=self.host, port=self.port, db=self.dbname)

    def get_conn(self):
        '''Get the connection to the database.'''

        return r.connect(host=bigchaindb.config['database']['host'],
                         port=bigchaindb.config['database']['port'],
                         db="restore_{}".format(bigchaindb.config['database']['name']))

    def write_block(self, block, durability='soft'):
        """Write a block to bigchain.

        Args:
            block (json): block to write to bigchain.
        """
        return self.backend.write_block(block, durability=durability)

    def write_vote(self, vote):
        """Write the vote to the database."""
        return self.backend.write_vote(vote)

    def drop(self, assume_yes=False):
        print(" drop database {}".format(self.dbname))
        rethinkdb_utils.drop(assume_yes=False)

    def create_database(self):
        print("create database {}".format(self.dbname))
        rethinkdb_utils.init_database()

    def exists_database(self, dbname=None):
        if not dbname:
            dbname = self.dbname
        return rethinkdb_utils.exists_database(dbname)

if __name__=="__main__":
    rq = RethinkdbUtils()
    rq.drop()
    dbname = rq.dbname
    exists_db = rethinkdb_utils.exists_database(dbname)
    if not exists_db:
        rq.create_database()

    exit("init success")
