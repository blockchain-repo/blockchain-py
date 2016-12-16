from ul_tests.db.utils_localdb import LocaldbUtils


if __name__ == "__main__":

    ld = LocaldbUtils()
    conn_block_records = ld.get_conn('block_records')
    records = ld.get_all_records(conn_block_records,show_only=False)

    for record in records:
        print(record)


    total_records = ld.get_records_count(conn_block_records)
    print("total_records is {}".format(total_records))

    ld.close(conn_block_records)