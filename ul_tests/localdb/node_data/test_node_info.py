from ul_tests.db.utils_localdb import LocaldbUtils


if __name__ == "__main__":

    ld = LocaldbUtils()

    conn_node_info = ld.get_conn('node_info')
    records = ld.get_all_records(conn_node_info,show_only=False)

    for record in records:
        print(record)

    total_records = ld.get_records_count(conn_node_info)
    print("total_records is {}".format(total_records))

    ld.close(conn_node_info)