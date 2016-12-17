
import plyvel as l
import rapidjson
import sys
import os
import logging

from extend.localdb import config

logger = logging.getLogger(__file__)

class LocaldbUtils():
    """To test the localdb
    """

    def __init__(self):
        self.root = config['database']['path']
        self.tables = config['database']['tables']
        self.node_host = None

    def check_dirs_exist(self, *args):
        exist_path = os.path.exists()
        if not exist_path:
            logger.error("localdb dirs is not exist!")
            return False
        return True

    def check_conn_free(self, close_flag=True, *args):
        conn_names = self.tables
        include = len(set(args).difference(conn_names)) == 0
        if args and include:
            conn_names = args
        conn = None
        conn_name_temp = None
        try:
            for conn_name in conn_names:
                conn_name_temp = conn_name
                conn = l.DB(self.root + conn_name + "/")
                self.close(conn)
        except (Exception,IOError) as msg:
            logger.error("Conn {} is busy or can`t access, you must close it and check that"
                         ",the local dirs have not content also can cause the failure!"
                         "\nYou should read the error msg: {}".format(conn_name_temp, msg))
            if close_flag:
                self.close(conn)
            return False
        return True

    def get_conn(self,conn_name):
        if conn_name in self.tables:
            try:
                return l.DB(self.root + conn_name + "/")

                #  snapshot has no attribute 'prefixed_db', so we use normal
                # return l.DB(self.root + conn_name + "/").snapshot()
            except Exception as localdb_utils_ex:
                print("LocalDBUtils.get_conn() exception {}".format(localdb_utils_ex))
                return None

    def close(self,conn):
        if conn:
            conn.close()

    def close_conn(self,*args):
        for arg in args:
            self.close(arg)

    def get_restore_node_info(self):
        conn_node_info = self.get_conn('node_info')
        conn_block_header = self.get_conn('block_header')
        conn_vote_header = self.get_conn('vote_header')

        host = self.get_val(conn_node_info,'host')
        public_key = self.get_val(conn_node_info,'public_key')
        restart_times = int(self.get_val(conn_node_info,'restart_times'))
        block_num = int(self.get_val(conn_block_header,'current_block_num'))
        vote_num = int(self.get_val(conn_vote_header,'current_vote_num'))

        self.close_conn(conn_node_info, conn_block_header, conn_vote_header)
        self.node_host = host
        response = {
            "host": host,
            "pubkey": public_key,
            "restart_times": restart_times,
            "block_num": block_num,
            "vote_num": vote_num
        }
        return response

    def get_restore_block_info(self,block_num):
        conn_block_records = self.get_conn('block_records')
        conn_block = self.get_conn('block')
        conn_vote = self.get_conn('vote')
        conn_block_header = self.get_conn('block_header')

        block_id = self.get_val(conn_block_records, block_num)
        block = self.get_obj(conn_block, block_id)
        block_votes = self.get_obj_prefix(conn_vote, prefix=block_id)
        total_block_num = int(self.get_val(conn_block_header, 'current_block_num'))

        self.close_conn(conn_block_records, conn_block, conn_vote, conn_block_header)
        response = {
            "host":self.node_host,
            "block_num": block_num,
            "total_block_num": total_block_num,
            "block_id":block_id,
            "block": block,
            "votes": block_votes,
            "votes_count": len(block_votes),
            "desc": "The node block_num {}, progress {:<8},".format(block_num,"%0.2f%%" %(block_num/total_block_num*100))
        }

        return response

    def get_val(self,conn,key):
        """Get the value with the special key

        Args:
            conn: the leveldb dir pointer
            key:

        Returns:
             the string
        """

        if conn:
            bytes_val = conn.get(bytes(str(key), config['encoding']))
            if bytes_val:
                return bytes(bytes_val).decode(config['encoding'])
            else:
                return None

    def get_obj(self, conn, key):
        """Get the value with the special key

        Args:
            conn: the leveldb dir pointer
            key:

        Returns:
             the string
        """

        if conn:
            bytes_val = conn.get(bytes(str(key), config['encoding']))
            if bytes_val:
                return rapidjson.loads(bytes(bytes_val).decode(config['encoding']))
            else:
                return None

    def get_obj_prefix(self, conn, prefix=None):
        """Get the value with the special prefix

        Args:
           conn: the leveldb dir pointer
           prefix: full key must be like pfefix+.*
        Returns:
            the string
        """

        if conn:
            result = {}
            for key, value in conn.iterator(prefix=bytes(str(prefix), config['encoding'])):
                key = bytes(key).decode(config['encoding'])
                value = rapidjson.loads(bytes(value).decode(config['encoding']))
                result[key] = value
            return result
        else:
            return None

    def get_val_prefix(self,conn,prefix=None):
        """Get the value with the special prefix

        Args:
           conn: the leveldb dir pointer
           prefix: full key must be like pfefix+.*
        Returns:
            the string
        """

        if conn:
            result = {}
            for key, value in conn.iterator(prefix=bytes(str(prefix), config['encoding'])):
                key = bytes(key).decode(config['encoding'])
                value = bytes(value).decode(config['encoding'])
                result[key] = value
            return result
        else:
            return None


    def __convert_to_obj(self,json_str_bytes):
        """Convert the input[must be (b`K,b`V) format]

        Args:
            json_str_bytes

        Return:

        """

        if len(json_str_bytes) != 2:
            return None
        key = json_str_bytes[0]
        val = json_str_bytes[1]

        key = bytes(key).decode('utf-8')
        if json_str_bytes:
            try:
                return key,rapidjson.loads(bytes(val).decode('utf-8'))
            except Exception as convet_ex:
                is_obj = False
                return key,bytes(val).decode('utf-8')


    def get_records_count(self,conn):
        """Get the localdb records count

        Args:
            conn: dirs or db

        Return:
           the count of the db records
        """

        if not conn:
            return 0

        raw_iterator = conn.raw_iterator()  # invalid,must move to the first
        if raw_iterator:
            raw_iterator.seek_to_first()
        else:
            return 0

        count = 0

        while raw_iterator.valid() and raw_iterator.item():
            count = count + 1
            item = raw_iterator.item()
            # Only move ,no returnVal
            raw_iterator.next()

        return count


    def get_all_records(self,conn,show_only=False,limit=None):
        if not conn:
            return None

        raw_iterator = conn.raw_iterator()  # invalid,must move to the first
        if raw_iterator:
            raw_iterator.seek_to_first()
        else:
            return None

        count = 0

        if limit and limit <= 0:
            return None

        if limit and limit >= 1:
            if show_only:
                while raw_iterator.valid() and raw_iterator.item():
                    count = count + 1
                    item = raw_iterator.item()  # json_str_bytes,k-v
                    item_key, item_val = self.__convert_to_obj(item)
                    print('The current record {}th,  [{}={}]\n'.format(count, item_key, item_val))
                    # Only move ,no returnVal
                    raw_iterator.next()
                    if count == limit:
                        break
                print('The total records is: {}'.format(count))
            else:
                result = []
                while raw_iterator.valid() and raw_iterator.item():
                    count = count + 1
                    item = raw_iterator.item()  # json_str_bytes,k-v
                    item_key, item_val = self.__convert_to_obj(item)
                    resut_item = dict()
                    resut_item[item_key] = item_val
                    result.append(resut_item)
                    del resut_item
                    # Only move ,no returnVal
                    raw_iterator.next()
                    if count == limit:
                        break
                return result
        else:
            if show_only:
                while raw_iterator.valid() and raw_iterator.item():
                    count = count + 1
                    item = raw_iterator.item()  # json_str_bytes,k-v
                    item_key,item_val = self.__convert_to_obj(item)
                    print('The current record {}th,  [{}={}]\n'.format(count,item_key,item_val))
                    # Only move ,no returnVal
                    raw_iterator.next()
                print('The total records is: {}'.format(count))
            else:
                result = []
                while raw_iterator.valid() and raw_iterator.item():
                    count = count + 1
                    item = raw_iterator.item()  # json_str_bytes,k-v
                    item_key, item_val = self.__convert_to_obj(item)
                    resut_item = dict()
                    resut_item[item_key] = item_val
                    result.append(resut_item)
                    del resut_item
                    # Only move ,no returnVal
                    raw_iterator.next()
                return result
