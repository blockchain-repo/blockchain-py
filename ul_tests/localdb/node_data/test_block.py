
from ul_tests.db.utils_localdb import LocaldbUtils


if __name__ == "__main__":

    ld = LocaldbUtils()

    block_conn = ld.get_conn('block')

    # all_blocks = ld.get_all_records(block_conn,show_only=False,limit=2)
    # for block in all_blocks:
    #     print("{}\n".format(block))


    # block_key = "000f39c7bd17ca45eabdfdb2565f267249358c701339f0f8006a32788431577b"
    # block_key = "00cd18127c78a49be8565cf4c0d123913cd3fa8f4b6993a801fb75f455e55913"
    # block_key_val = ld.get_val(block_conn,block_key)
    # print(block_key_val)


    block_key_prefix = "c2"
    block_dict = ld.get_val_prefix(block_conn,block_key_prefix)

    for key,block in block_dict.items():
        print("key={},\nblock={}\n".format(key,block))

    print("result[total={},prefix={}]".format(len(block_dict),block_key_prefix))

    total_block = ld.get_records_count(block_conn)
    print("total_block is {}".format(total_block))

    ld.close(block_conn)