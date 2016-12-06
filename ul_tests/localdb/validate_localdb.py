

from ul_tests.db.utils_localdb import LocaldbUtils
from ul_tests.db.utils_rethinkdb import RethinkdbUtils


class LocaldbValite():
    """Valide the localdb data is valide"""

    def __init__(self):
        self.rq = RethinkdbUtils()
        self.ldb = LocaldbUtils()
        self.conn_block = self.ldb.get_conn('block')
        self.conn_block_header = self.ldb.get_conn('block_header')
        self.conn_vote = self.ldb.get_conn('vote')
        self.conn_vote_header = self.ldb.get_conn('vote_header')
        self.conn_block_records = self.ldb.get_conn('block_records')


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
                .format(localdb_records_count, rethinkdb_records_count, header_count)
            isOK = False

            if localdb_records_count == rethinkdb_records_count \
                    and rethinkdb_records_count == header_count:
                isOK = True
        return isOK,result


if __name__ == "__main__":

    lv = LocaldbValite()
    block_isOk,block_check = lv.check_records('bigchain',lv.conn_block,lv.conn_block_header,'current_block_num')
    votes_isOk,votes_check = lv.check_records('votes',lv.conn_vote,lv.conn_vote_header,'current_vote_num')

    if block_isOk and votes_isOk:
        print("The localdb and rethinkdb is the same! The result as follows:\n{}\t\n{}".format(block_check,votes_check))
    else:
        print("The localdb and rethinkdb is not the same! The result as follows:\n{}\t\n{}".format(block_check, votes_check))