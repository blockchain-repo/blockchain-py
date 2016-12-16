from ul_tests.db.utils_localdb import LocaldbUtils


if __name__ == "__main__":

    ld = LocaldbUtils()
    # 1. vote header
    conn_header = ld.get_conn('block_header')
    records = ld.get_all_records(conn_header,show_only=False)

    for record in records:
        print(record)

    # block_num = ld.get_val(conn_header,'block_num')
    # current_block_id = ld.get_val(conn_header,'current_block_id')
    # current_block_timestamp = ld.get_val(conn_header,'current_block_timestamp')
    # genesis_block_id = ld.get_val(conn_header,'genesis_block_id')
    #
    # result = "block_num={}\ncurrent_block_id={}\ncurrent_block_timestamp={}\ngenesis_block_id={}\n"\
    #     .format(block_num,current_block_id,current_block_timestamp,genesis_block_id)
    #
    # print(result)

    total_records = ld.get_records_count(conn_header)
    print("total_records is {}".format(total_records))

    ld.close(conn_header)