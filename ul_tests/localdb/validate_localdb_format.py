
import argparse
from ul_tests.db.utils_localdb import LocaldbUtils
from ul_tests.db.utils_rethinkdb import RethinkdbUtils


class LocaldbValite():
    """Valide the localdb data is valide"""

    def __init__(self):
        self.rq = RethinkdbUtils()
        self.ldb = LocaldbUtils()
        self.conn_bigchain = self.ldb.get_conn('bigchain')
        self.conn_block_header = self.ldb.get_conn('block_header')
        self.conn_votes = self.ldb.get_conn('votes')
        self.conn_vote_header = self.ldb.get_conn('vote_header')


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

        result = "[localdb={}, rethinkdb={}, header={}]".format(localdb_records_count, rethinkdb_records_count, header_count)
        isOK = False

        if localdb_records_count == rethinkdb_records_count\
                 and rethinkdb_records_count == header_count:
            isOK = True

        return isOK,result


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Validate localdb & format result output")

    parser.add_argument('-r', action="store_true",help='Output the localdb and rethinkdb result only.')
    parser.add_argument('-o', action="store_true",help='Output the votes & transactions info from rethinkdb by order asc')
    parser.add_argument('-v', action="store_true",help='Output the block_votes info from rethinkdb')
    parser.add_argument('-t', action="store_true",help='Output the block_transactions info from rethinkdb')

    args = parser.parse_args()

    result_only = args.r
    block_votes = args.v
    block_txs = args.t

    if not (result_only or block_votes or block_txs):
        result_only = True


    lv = LocaldbValite()


    ############################################### check_records ####################################################
    if result_only:
        block_isOk,block_check = lv.check_records('bigchain',lv.conn_bigchain,lv.conn_block_header,'block_num')
        votes_isOk,votes_check = lv.check_records('votes',lv.conn_votes,lv.conn_vote_header,'vote_num')

        if block_isOk and votes_isOk:
            print("The localdb and rethinkdb is the same! The result as follows:\nblock\t{}\nvotes\t{}".format(block_check,votes_check))
        else:
            print("The localdb and rethinkdb is not the same! The result as follows:\nblock\t{}\nvotes\t{}".format(block_check, votes_check))


    ############################################### get_blocks_votes_count ####################################################
    if block_votes:
        block_count, blocks_votes_count, block_votes_count_list = lv.rq.get_blocks_votes_count(order_by=True)
        print("get_blocks_votes_count query result: total blocks={},total votes={}".format(block_count,blocks_votes_count))

        block_votes_count_number = 0
        for block_votes_count in block_votes_count_list:
            block_votes_count_number += 1
            for block_id,votes_count in block_votes_count.items():
                print("block_number={}\tblock_id={}\tblock_votes_count={}".format(block_votes_count_number,block_id,votes_count))


    ############################################### get_txs_count ####################################################
    if block_votes:
        block_count, txs_count, block_txs_count_list = lv.rq.get_txs_count(order_by=True)
        print("get_txs_count query result: total blocks={},total txs={}".format(block_count,
                                                                                           txs_count))

        block_txs_count_number = 0
        for block_txs_count in block_txs_count_list:
            block_txs_count_number += 1
            for block_id, txs_count in block_txs_count.items():
                print("block_number={}\tblock_id={}\tblock_txs_count={}".format(block_txs_count_number, block_id,
                                                                                  txs_count))