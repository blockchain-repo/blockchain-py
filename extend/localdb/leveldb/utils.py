"""Utils to initialize and drop the localdb [levelDB]."""
# bytes can only contain ASCII literal characters.

import plyvel as l
import os
from extend.localdb import config

import logging

logger = logging.getLogger(__name__)


class LocalBlock(object):
    """Singleton LocalBlock encapsulates leveldb`s base ops base on plyvel.

    Warn:
        1. leveldb [Only support a single process (possibly multi-threaded) can access a particular database at a time.];
        2. multi-thread [Singleton can deal.];
        3. it`s only use for leveldb dir [block, block_header, block_records] op.

    Attributes:
        conn: The dict include the dir link config['database']['tables'].

    """

    # Only run once with process start.

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            logger.info('init localdb dirs [block, block_header, block_records] start')
            cls.instance = super(LocalBlock, cls).__new__(cls)
            database = config['database']
            parent_dir = database['path']
            if not os.path.exists(parent_dir):
                logging.error("localdb dirs is not exist!")
                raise IOError("localdb dirs is not exist, you should create dirs {} for "
                              "localdb grant acess for current user!".format(parent_dir))
            block_size = database['block_size']
            write_buffer_size = database['write_buffer_size']
            max_open_files = database['max_open_files']
            lru_cache_size = database['lru_cache_size']
            cls.instance.conn = dict()
            try:
                cls.instance.conn['node_info'] = l.DB(parent_dir + 'node_info/', create_if_missing=True, write_buffer_size=write_buffer_size,
                                                  block_size=block_size, max_open_files=max_open_files,lru_cache_size=lru_cache_size)
                cls.instance.conn['block'] = l.DB(parent_dir + 'block/', create_if_missing=True, write_buffer_size=write_buffer_size,
                                                     block_size=block_size, max_open_files=max_open_files, lru_cache_size=lru_cache_size)
                cls.instance.conn['block_header'] = l.DB(parent_dir + 'block_header/', create_if_missing=True, write_buffer_size=write_buffer_size,
                                                   block_size=block_size, max_open_files=max_open_files, lru_cache_size=lru_cache_size)
                cls.instance.conn['block_records'] = l.DB(parent_dir + 'block_records/', create_if_missing=True, write_buffer_size=write_buffer_size,
                                                     block_size=block_size, max_open_files=max_open_files, lru_cache_size=lru_cache_size)
            except IOError as msg:
                logger.error("You can`t acess the local data {}".format(parent_dir))
                exit(-1)

            logger.info('init localdb dirs [block, block_header, block_records] end')

        return cls.instance


class LocalVote(object):
    """Singleton LocalVote encapsulates leveldb`s base ops base on plyvel.

    Warn:
        1. leveldb [Only support a single process (possibly multi-threaded) can access a particular database at a time.];
        2. multi-thread [Singleton can deal.];
        3. it`s only use for leveldb dir [vote, vote_header] op.

    Attributes:
        conn: The dict include the dir link config['database']['tables'].
    """

    # Only run once with process start.

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            logger.info('init localdb dirs [vote, vote_header] start')
            cls.instance = super(LocalVote, cls).__new__(cls)
            database = config['database']
            parent_dir = database['path']
            if not os.path.exists(parent_dir):
                logging.error("localdb dirs is not exist!")
                raise IOError("localdb dirs is not exist, you should create dirs {} for "
                              "localdb grant acess for current user!".format(parent_dir))
            block_size = database['block_size']
            write_buffer_size = database['write_buffer_size']
            max_open_files = database['max_open_files']
            lru_cache_size = database['lru_cache_size']
            cls.instance.conn = dict()
            try:
                cls.instance.conn['vote'] = l.DB(parent_dir + 'vote/', create_if_missing=True,write_buffer_size=write_buffer_size,
                                                  block_size=block_size,max_open_files=max_open_files,lru_cache_size=lru_cache_size)
                cls.instance.conn['vote_header'] = l.DB(parent_dir + 'vote_header/', create_if_missing=True,write_buffer_size=write_buffer_size,
                                                         block_size=block_size, max_open_files=max_open_files,lru_cache_size=lru_cache_size)
            except IOError as msg:
                logger.error("You can`t acess the local data {}".format(parent_dir))
                exit(-1)
            logger.info('init localdb dirs [vote, vote_header] end')

        return cls.instance


def close(conn):
    """Close the conn.
    Args:
        conn: the leveldb dir pointer.

    Returns:

    """

    if conn:
        conn.close()
        logger.info('leveldb close conn ... {}'.format(conn))


def close_all():
    """Close all databases dir."""

    tables = config['database']['tables']
    logger.info('leveldb close all databases {}'.format(tables))
    result = []
    for table in tables:
        if table is not None:
            try:
                dir = config['database']['path']+table+'/'
                close(dir)
                result.append(dir)
            except:
                # print(table + ' is not exist')
                continue
    logger.info('leveldb close all...{}'.format(result))


def get_conn(name,prefix_db=None):
    """Insert the value with the special key.

    Args:
        name: the leveldb dir name.
        prefix_db: you want get the conn from which local dir
    Returns:
        the leveldb dir pointer.
    """
    if prefix_db is None or prefix_db not in config['database']['tables']:
        raise BaseException("Ambigous localdb conn, it should be explicit!")

    if prefix_db in ("node_info","block","block_header","block_records"):
        return LocalBlock().conn[name]

    if prefix_db in ("vote",'vote_header'):
        return LocalVote().conn[name]

    return BaseException("Error prefix_db {}!".format(prefix_db))


def insert(conn,key,value,sync=False):
    """Insert the value with the special key.

      Args:
          conn: the leveldb dir pointer.
          key:
          sync(bool) – whether to use synchronous writes.

      Returns:

    """

    # logger.info('leveldb insert...' + str(key) + ":" +str(value))
    conn.put(bytes(str(key),config['encoding']),bytes(str(value),config['encoding']),sync=sync)


def batch_insertOrUpdate(conn,dict,transaction=False,sync=False):
    """Batch insert or update the value with the special key in dict.

    Args:
        conn: the leveldb dir pointer.
        dict:
        transaction(bool) – whether to enable transaction-like behaviour when
        the batch is used in a with block.
        sync(bool) – whether to use synchronous writes.

    Returns:

    """

    with conn.write_batch(transaction=transaction,sync=sync) as b:
        for key in dict:
            # logger.warn('key: ' + str(key) + ' --- value: ' + str(dict[key]))
            b.put(bytes(str(key),config['encoding']),bytes(str(dict[key]),config['encoding']))


def delete(conn,key,sync=False):
    """Delete the value with the special key.

    Args:
        conn: the leveldb dir pointer.
        key:
        sync(bool) – whether to use synchronous writes.

    Returns:

    """

    # logger.info('leveldb delete...' + str(key) )
    conn.delete(bytes(str(key),config['encoding']),sync=sync)


def batch_delete(conn,dict,transaction=False,sync=False):
    """Batch delete the value with the special key in dict.

    Args:
        conn: the leveldb dir pointer.
        dict:
        transaction(bool) – whether to enable transaction-like behaviour when
        the batch is used in a with block.
        sync(bool) – whether to use synchronous writes.

    Returns:

    """

    with conn.write_batch(transaction=transaction,sync=sync) as b:
        for key,value in dict:
            b.delete(bytes(str(key),config['encoding']))


def update(conn,key,value,sync=False):
    """Update the value with the special key.

    Args:
        conn: the leveldb dir pointer.
        key:
        value(str) – value to set.
        sync(bool) – whether to use synchronous writes.

    Returns:

    """

    # logger.info('leveldb update...' + str(key) + ":" +str(value))
    conn.put(bytes(str(key),config['encoding']), bytes(str(value),config['encoding']),sync=sync)


def get(conn,key):
    """Get the value with the special key.

    Args:
        conn: the leveldb dir pointer.
        key:

    Returns:
        the string
    """

    # logger.info('leveldb get...' + str(key))
    # get the value for the bytes_key,if not exists return None
    # bytes_val = conn.get_property(bytes(key, config['encoding']))
    bytes_val = conn.get(bytes(str(key), config['encoding']))
    if bytes_val:
        return bytes(bytes_val).decode(config['encoding'])
    else:
        return None


def get_with_prefix(conn,prefix):
    """Get the records with the special prefix.

    block-v1=v1
    block-v2=v2
    block-v3=v3
    prefix = 'block'  => {'-v1':'v1','-v2':'v2','-v3':'v3'}
    prefix = 'block-' => {'v1':'v1','v2':'v2','v3':'v3'}

    Args:
        conn: the leveldb dir pointer.
        prefix: the key start with,before '-'.

    Returns:
        the dict
    """

    if conn:
        # logger.warn(str(conn) + ' , ' + str(prefix))
        result = {}
        for key, value in conn.iterator(prefix=bytes(str(prefix), config['encoding'])):
            key = bytes(key).decode(config['encoding'])
            value = bytes(value).decode(config['encoding'])
            result[key] = value
        return result
    else:
        return None


def get_withdefault(conn,key,default_value):
    """Get the value with the key.

    Args:
        conn: the leveldb dir pointer.
        key:
        default_value: if value is None,it will return.

    Returns:
        the string
    """

    # logger.info('leveldb get...' + str(key) + ",default_value=" + str(default_value))
    # get the value for the bytes_key,if not exists return defaule_value
    bytes_val = conn.get(bytes(str(key),config['encoding']),bytes(str(default_value),config['encoding']))
    # return bytes(bytes_val).decode(config['encoding'])
    # logger.info('leveldb get...' + str(key) + ",default_value=" + bytes(bytes_val).decode(config['encoding']))
    return bytes(bytes_val).decode(config['encoding'])