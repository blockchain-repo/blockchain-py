

import logging

import bigchaindb
import rethinkdb as r
import bigchaindb.config_utils
from bigchaindb import config_utils
from extend.localdb.restore.rethinkdb_utils import utils as rethinkdb_utils

logger = logging.getLogger(__name__)


class RethinkdbUtils():

    def __init__(self, host=None, port=None, dbname=None, backend=None):
        config_utils.autoconfigure()
        self.host = host or bigchaindb.config['database']['host']
        self.port = port or bigchaindb.config['database']['port']
        self.dbname = dbname or bigchaindb.config['database']['name']
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
        rethinkdb_utils.drop(assume_yes=assume_yes)

    def clear(self, dbname, *tables):
        rethinkdb_utils.clear(self.connection, dbname, tables)

    def create_database(self):
        print("create database {}".format(self.dbname))
        rethinkdb_utils.init_database()

    def exists_database(self, dbname=None):
        if not dbname:
            dbname = self.dbname
        return rethinkdb_utils.exists_database(dbname)

    def get_count(self, table,  dbname=None):
        if not dbname:
            dbname = self.dbname
        return rethinkdb_utils.get_count(dbname, table)

    def get_last_before_block_id(self,  dbname=None):
        if not dbname:
            dbname = self.dbname
        return rethinkdb_utils.get_last_before_block_id(dbname)

# if __name__=="__main__":
#     rq = RethinkdbUtils()
#     dbname = rq.dbname
#     exists_db = rq.exists_database('bigchain')
#     print("exists db {} {}".format(dbname, exists_db))
#     records_count = rq.get_count(table='bigchain', dbname=dbname)
#     print("records_count={}".format(records_count))
#     last_before_block_id = rq.get_last_before_block_id(dbname=dbname)
#     print("last_before_block_id={}".format(last_before_block_id))
#     # rq.drop()
#     # print("host={},port={},dbname={}".format(rq.host, rq.port, rq.dbname))
#     # rq.clear(dbname=dbname)
#     exists_db = rethinkdb_utils.exists_database(dbname)
#     if not exists_db:
#         rq.create_database()
#
#     exit("init success")
