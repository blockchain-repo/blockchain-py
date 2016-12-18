
from ul_tests.db.utils_localdb import LocaldbUtils

if __name__ == "__main__":

    ld = LocaldbUtils()
    # 1. vote header
    conn_header = ld.get_conn('vote_header')

    records = ld.get_all_records(conn_header,show_only=False)

    print(records)

    total_records = ld.get_records_count(conn_header)
    print("total_records is {}".format(total_records))

    ld.close(conn_header)