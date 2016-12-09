


import plyvel as l
import rapidjson

from extend.localdb import config


class LocaldbUtils():
    """To test the localdb
    """

    def __init__(self):
        self.root = config['database']['path']
        self.tables = config['database']['tables']

    def get_conn(self,conn_name):
        if conn_name in self.tables:
            try:
                return l.DB(self.root + conn_name + "/")

                #  snapshot has no attribute 'prefixed_db', so we use normal
                # return l.DB(self.root + conn_name + "/").snapshot()
            except Exception as localdb_utils_ex:
                print("LocalDBUtils.get_conn() exception {}".format(localdb_utils_ex))
                return None

    @staticmethod
    def close(conn):
        """Close the conn.
        Args:
            conn: the leveldb dir pointer.

        Returns:

        """

        if conn:
            conn.close()

    @staticmethod
    def get_val(conn,key):
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

    @staticmethod
    def get_val_prefix(conn,prefix=None):
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

    @staticmethod
    def __convert_to_obj(json_str_bytes):
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

    @staticmethod
    def get_records_count(conn):
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