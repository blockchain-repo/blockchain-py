

from ul_tests.db.utils_localdb import LocaldbUtils
from ul_tests.db.utils_rethinkdb import RethinkdbUtils


class LocaldbValidate():
    """Valide the localdb data is valid"""

    def __init__(self):
        self.rq = RethinkdbUtils()
        self.ldb = LocaldbUtils()
        self.conn_block = self.ldb.get_conn('block')
        self.conn_block_header = self.ldb.get_conn('block_header')
        self.conn_vote = self.ldb.get_conn('vote')
        self.conn_vote_header = self.ldb.get_conn('vote_header')
        self.conn_block_records = self.ldb.get_conn('block_records')
        self.conn_node_info = self.ldb.get_conn('node_info')


    def check_records(self,table,localdb_table_conn,localdb_header_conn,count_key):
        """check the records with rethinkdb and return the result

        Args:
            table:
            localdb_table_conn:
            localdb_header_conn:
            count_key:
        Return:
            isOk: is validate
            result: the result of this check
        """

        localdb_records_count = self.ldb.get_records_count(localdb_table_conn)
        rethinkdb_records_count = self.rq.get_counts(table)
        header_count = self.ldb.get_val(localdb_header_conn,count_key)

        if header_count and header_count.strip() != '':
            header_count = int(header_count)

        if header_count is None:
            header_count = 0

        if table == 'bigchain':
            block_records_count = lv.ldb.get_records_count(lv.conn_block_records)
            result = "block\t[rethinkdb={}, localdb={}, header={}, block_records={}]"\
                .format(rethinkdb_records_count, localdb_records_count, header_count, block_records_count)
            isOK = False

            if localdb_records_count == rethinkdb_records_count\
                     and rethinkdb_records_count == header_count\
                     and header_count == block_records_count:
                isOK = True
        else:
            result = "vote\t[rethinkdb={}, localdb={}, header={}]"\
                .format(rethinkdb_records_count, localdb_records_count, header_count)
            isOK = False

            if localdb_records_count == rethinkdb_records_count \
                    and rethinkdb_records_count == header_count:
                isOK = True
        return isOK,result

    def get_node_info(self):
        node_host = self.ldb.get_val(self.conn_node_info, "host")
        node_public_key = self.ldb.get_val(self.conn_node_info, "public_key")
        node_restart_times = self.ldb.get_val(self.conn_node_info, "restart_times")
        return node_host, node_public_key, node_restart_times

if __name__ == "__main__":

    lv = LocaldbValidate()
    block_isOk,block_check = lv.check_records('bigchain',lv.conn_block,lv.conn_block_header,'current_block_num')
    votes_isOk,votes_check = lv.check_records('votes',lv.conn_vote,lv.conn_vote_header,'current_vote_num')
    node_host, node_public_key, node_restart_times = lv.get_node_info()
    lv.ldb.close(lv.conn_block)
    lv.ldb.close(lv.conn_block_header)
    lv.ldb.close(lv.conn_block_records)
    lv.ldb.close(lv.conn_vote)
    lv.ldb.close(lv.conn_vote_header)
    lv.ldb.close(lv.conn_node_info)
    if block_isOk and votes_isOk:
        print("The localdb and rethinkdb is the same! The result as follows:\n{}\t\n{}".format(block_check,votes_check))
    else:
        print("The localdb and rethinkdb is not the same! The result as follows:\n{}\t\n{}".format(block_check, votes_check))
    print("The node info is: [host={}, public_key={}, restart_times={}]".format(node_host,node_public_key,node_restart_times))