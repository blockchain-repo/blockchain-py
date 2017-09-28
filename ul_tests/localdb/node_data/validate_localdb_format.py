import argparse
from ul_tests.db.utils_localdb import LocaldbUtils
from ul_tests.db.utils_rethinkdb import RethinkdbUtils
import time

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
        node_host = self.ldb.get_val(self.conn_node_info,"host")
        node_public_key = self.ldb.get_val(self.conn_node_info,"public_key")
        node_restart_times = self.ldb.get_val(self.conn_node_info,"restart_times")
        return node_host, node_public_key, node_restart_times

    def close_conn(self,*args):
        for arg in args:
            self.ldb.close(arg)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Validate localdb & format result output")

    parser.add_argument('-a', action="store_true",help='show the votes & txs detail info, if with -vt')
    parser.add_argument('-b', action="store_true",help='show the statics info above in the file tail')
    parser.add_argument('-i', action="store_true",help='ignore the partial info[node_info and so on], if have the parameter')
    parser.add_argument('-n', action="store_true",help='show the node info')
    parser.add_argument('-o', action="store_true",help='output the votes & transactions info from rethinkdb by order asc')
    parser.add_argument('-q', action="store_true",help='hide the help info')
    parser.add_argument('-r', action="store_true",help='output the localdb and rethinkdb check result')
    parser.add_argument('-t', action="store_true",help='output the block_transactions info from rethinkdb')
    parser.add_argument('-v', action="store_true",help='output the block_votes info from rethinkdb')

    args = parser.parse_args()

    show_votes_txs_detail = args.a
    result_only = args.r
    block_votes = args.v
    block_txs = args.t
    order_block_votes = args.o
    ignore_diff_infos = args.i
    tail_infos = args.b
    node_info = args.n
    hide_format_help = args.q

    if not (result_only or block_votes or block_txs):
        result_only = True

    lv = LocaldbValidate()

    statics_info = ""
    if not ignore_diff_infos:
        #localtime_info = "localtime[{}]\n".format(time.localtime())
        localtime_info = "localtime[{}]\n".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        print(localtime_info)
        statics_info += localtime_info


    cost_time = time.time()
    ############################################### check_records ####################################################
    if result_only:
        block_isOk,block_check = lv.check_records('bigchain',lv.conn_block,lv.conn_block_header,'current_block_num')
        votes_isOk,votes_check = lv.check_records('votes',lv.conn_vote,lv.conn_vote_header,'current_vote_num')

        if block_isOk and votes_isOk:
            check_records_info = "The localdb and rethinkdb is the same! The result as follows:\n{}\n{}".format(block_check,votes_check)
        else:
            check_records_info = "The localdb and rethinkdb is not the same! The result as follows:\n{}\n{}".format(block_check, votes_check)
        print(check_records_info)
        statics_info += check_records_info

    ############################################### get_blocks_votes_count ####################################################
    if block_votes:
        if order_block_votes:
            block_count, blocks_votes_count, block_votes_count_list = lv.rq.get_blocks_votes_count(order_by=True)
        else:
            block_count, blocks_votes_count, block_votes_count_list = lv.rq.get_blocks_votes_count(order_by=False)

        get_blocks_votes_count_info = "\nget_blocks_votes_count query result: total blocks={},total votes={}".format(block_count,blocks_votes_count)
        print(get_blocks_votes_count_info)
        statics_info += get_blocks_votes_count_info

        block_votes_count_number = 0
        for block_votes_count in block_votes_count_list:
            block_votes_count_number += 1
            if show_votes_txs_detail:
                for block_id,votes_count in block_votes_count.items():
                    print("block_number={:<7}\tblock_id={}\tblock_votes_count={}".format(block_votes_count_number,block_id,votes_count))


    ############################################### get_txs_count ####################################################
    if block_txs:
        if order_block_votes:
            block_count, txs_count, block_txs_count_list = lv.rq.get_txs_count(order_by=True)
        else:
            block_count, txs_count, block_txs_count_list = lv.rq.get_txs_count(order_by=False)

        get_txs_count_info = "\nget_txs_count query result: total blocks={},total txs={}".format(block_count,txs_count)
        print(get_txs_count_info)
        statics_info += get_txs_count_info

        block_txs_count_number = 0
        for block_txs_count in block_txs_count_list:
            block_txs_count_number += 1
            if show_votes_txs_detail:
                for block_id, txs_count in block_txs_count.items():
                    print("block_number={:<7}\tblock_id={}\tblock_txs_count={}".format(block_txs_count_number, block_id,
                                                                                txs_count))

    cost_time = time.time() - cost_time
    if ignore_diff_infos:
        if hide_format_help:
            parameters_info = "\nThe op with parameters[{}]\n".format(args)
        else:
            parameters_info = "\nThe op with parameters[{}]\n{}".format(args, parser.format_help())

        print(parameters_info)
        statics_info += "\nThe op with parameters[{}]\n".format(args)
    else:
        ############################################### get node info ####################################################
        if node_info:
            node_host, node_public_key, node_restart_times = lv.get_node_info()
            get_node_info = "\nThe node info is: [host={}, public_key={}, restart_times={}]\n" \
                .format(node_host, node_public_key, node_restart_times)
            print(get_node_info)
            statics_info += get_node_info

        if hide_format_help:
            parameters_info = "\nThe op cost time {}s, with parameters[{}]\n".format(cost_time, args)
        else:
            parameters_info = "\nThe op cost time {}s, with parameters[{}]\n{}".format(cost_time, args,
                                                                                       parser.format_help())
        print(parameters_info)
        statics_info += "\nThe op cost time {}s, with parameters[{}]\n".format(cost_time, args)

    if tail_infos:
       print("The statics info detail as follows:\n{}".format(statics_info))
    lv.close_conn(lv.conn_block,lv.conn_block_header,lv.conn_block_records,lv.conn_vote,lv.conn_vote_header,lv.conn_node_info)