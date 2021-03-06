"""Utils to initialize and drop the database."""

import time
import logging

from bigchaindb.common import exceptions
import rethinkdb as r

import bigchaindb

logger = logging.getLogger(__name__)


class Connection:
    """This class is a proxy to run queries against the database,
    it is:
    - lazy, since it creates a connection only when needed
    - resilient, because before raising exceptions it tries
      more times to run the query or open a connection.
    """

    def __init__(self, host=None, port=None, db=None, max_tries=3):
        """Create a new Connection instance.

        Args:
            host (str, optional): the host to connect to.
            port (int, optional): the port to connect to.
            db (str, optional): the database to use.
            max_tries (int, optional): how many tries before giving up.
        """

        self.host = host or bigchaindb.config['database']['host']
        self.port = port or bigchaindb.config['database']['port']
        self.db = db or bigchaindb.config['database']['name']
        self.max_tries = max_tries
        self.conn = None

    def run(self, query):
        """Run a query.

        Args:
            query: the RethinkDB query.
        """

        if self.conn is None:
            self._connect()

        for i in range(self.max_tries):
            try:
                return query.run(self.conn)
            except r.ReqlDriverError as exc:
                if i + 1 == self.max_tries:
                    raise
                else:
                    self._connect()

    def _connect(self):
        for i in range(self.max_tries):
            try:
                self.conn = r.connect(host=self.host, port=self.port,
                                      db=self.db)
            except r.ReqlDriverError as exc:
                if i + 1 == self.max_tries:
                    raise
                else:
                    time.sleep(2 ** i)


def get_backend(host=None, port=None, db=None):
    '''Get a backend instance.'''

    from extend.localdb.restore.rethinkdb_utils.backends import rethinkdb

    # NOTE: this function will be re-implemented when we have real
    # multiple backends to support. Right now it returns the RethinkDB one.
    return rethinkdb.RethinkDBBackend(host=host or bigchaindb.config['database']['host'],
                                      port=port or bigchaindb.config['database']['port'],
                                      db=db or bigchaindb.config['database']['name'])


def get_conn(db=None):
    '''Get the connection to the database.'''

    return r.connect(host=bigchaindb.config['database']['host'],
                     port=bigchaindb.config['database']['port'],
                     db=db or bigchaindb.config['database']['name'])


def get_database_name(db=None):
    return db or bigchaindb.config['database']['name']


def create_database(conn, dbname):
    if r.db_list().contains(dbname).run(conn):
        raise exceptions.DatabaseAlreadyExists('Database `{}` already exists'.format(dbname))

    logger.info('Create database `%s`.', dbname)
    r.db_create(dbname).run(conn)


def exists_database(dbname):
    conn = get_conn()
    if r.db_list().contains(dbname).run(conn):
        return True
    else:
       return False


def create_table(conn, dbname, table_name):
    logger.info('Create `%s` table.', table_name)
    # create the table
    r.db(dbname).table_create(table_name).run(conn)


def create_bigchain_secondary_index(conn, dbname):
    logger.info('Create `bigchain` secondary index.')
    # to order blocks by timestamp
    r.db(dbname).table('bigchain') \
        .index_create('block_timestamp', r.row['block']['timestamp']) \
        .run(conn)
    # to query the bigchain for a transaction id
    r.db(dbname).table('bigchain') \
        .index_create('transaction_id',
                      r.row['block']['transactions']['id'], multi=True) \
        .run(conn)
    # secondary index for payload data by UUID
    r.db(dbname).table('bigchain') \
        .index_create('metadata_id',
                      r.row['block']['transactions']['transaction']['metadata']['id'], multi=True) \
        .run(conn)
    # secondary index for asset uuid
    r.db(dbname).table('bigchain') \
        .index_create('asset_id',
                      r.row['block']['transactions']['transaction']['asset']['id'], multi=True) \
        .run(conn)

    # wait for rethinkdb to finish creating secondary indexes
    r.db(dbname).table('bigchain').index_wait().run(conn)


def create_backlog_secondary_index(conn, dbname):
    logger.info('Create `backlog` secondary index.')
    # to order transactions by timestamp
    r.db(dbname).table('backlog') \
        .index_create('transaction_timestamp',
                      r.row['transaction']['timestamp']) \
        .run(conn)
    # compound index to read transactions from the backlog per assignee
    r.db(dbname).table('backlog') \
        .index_create('assignee__transaction_timestamp',
                      [r.row['assignee'], r.row['transaction']['timestamp']]) \
        .run(conn)

    # wait for rethinkdb to finish creating secondary indexes
    r.db(dbname).table('backlog').index_wait().run(conn)


def create_votes_secondary_index(conn, dbname):
    logger.info('Create `votes` secondary index.')

    # to order votes by timestamp
    r.db(dbname).table('votes') \
        .index_create('vote_timestamp', r.row['vote']['timestamp']) \
        .run(conn)

    # compound index to order votes by block id and node
    r.db(dbname).table('votes') \
        .index_create('block_and_voter',
                      [r.row['vote']['voting_for_block'],
                       r.row['node_pubkey']]) \
        .run(conn)

    # wait for rethinkdb to finish creating secondary indexes
    r.db(dbname).table('votes').index_wait().run(conn)


def init_database(db=None):
    """use the special db name init it

    :param db:
    :return:
    """
    conn = get_conn(db=db)
    dbname = get_database_name(db=db)
    create_database(conn, dbname)

    table_names = ['bigchain', 'backlog', 'votes', 'heartbeat', 'reassignnode', 'rewrite']
    for table_name in table_names:
        create_table(conn, dbname, table_name)

    create_bigchain_secondary_index(conn, dbname)
    create_backlog_secondary_index(conn, dbname)
    create_votes_secondary_index(conn, dbname)
    logger.info('Init {} Done, have fun!'.format(dbname))


def get_count(dbname, table):
    """get the records count in table
    :param dbname:
    :param table:
    :return:
    """
    table_names = ['bigchain', 'backlog', 'votes', 'heartbeat', 'reassignnode', 'rewrite']
    conn = get_conn(db=dbname)
    if table in table_names:
        return r.db(dbname).table(table).count().run(conn)
    else:
        return -1


def get_last_before_block_id(dbname):
    """get the last block`s id in table
    :param dbname:
    :param table:
    :return:
    """
    conn = get_conn(db=dbname)
    try:
        return r.db(dbname).table('bigchain').order_by(index=r.desc('block_timestamp')).nth(1)['id']\
        .default(None).run(conn)
    except:
        return None


def clear(conn, dbname, tables):
    """clear the database data

    :param conn:
    :param dbname:
    :param tables:(tuple or list ) str
    :return:
    """
    table_names = ['bigchain', 'backlog', 'votes', 'heartbeat', 'reassignnode', 'rewrite']
    conn = get_conn(db=dbname)
    table_in_names = dict()
    if not tables:
        for table in table_names:
            result = r.db(dbname).table(table).delete().run(conn)
            table_in_names[table] = result['deleted']
    else:
        if isinstance(tables, list):
            for table in tables:
                if table in table_names:
                    result = r.db(dbname).table(table).delete().run(conn)
                    table_in_names[table] = result['deleted']
        elif isinstance(tables, tuple):
            for table in tables:
                if table in table_names:
                    result = r.db(dbname).table(table).delete().run(conn)
                    table_in_names[table] = result['deleted']
        else :
            if tables in table_names:
                result = r.db(dbname).table(tables).delete().run(conn)
                table_in_names[tables] = result['deleted']
    print("clear database {} tables {}".format(dbname, table_in_names))


def drop(assume_yes=False):
    dbname = get_database_name()
    conn = get_conn()
    if assume_yes:
        response = 'y'

    else:
        response = input('Do you want to drop `{}` database? [y/n]: '.format(dbname))

    if response == 'y':
        try:
            logger.info('Drop database `%s`', dbname)
            r.db_drop(dbname).run(conn)
            logger.info('Done.')
        except r.ReqlOpFailedError:
            raise exceptions.DatabaseDoesNotExist('Database `{}` does not exist'.format(dbname))

    else:
        logger.info('Drop aborted')
