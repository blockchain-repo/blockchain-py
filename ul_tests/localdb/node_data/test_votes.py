
from ul_tests.db.utils_localdb import LocaldbUtils


if __name__ == "__main__":

    ld = LocaldbUtils()

    votes_conn = ld.get_conn('vote')

    # all_votes = ld.get_all_records(votes_conn,show_only=False)
    # print(all_votes)

    # vote_key = "000f39c7bd17ca45eabdfdb2565f267249358c701339f0f8006a32788431577b-akBGowqvc8WRQj5PxfN6zY9iNhkN7P87M99Hd4nHuBX"
    #
    # vote_key_val = ld.get_val(votes_conn,vote_key)
    # print(vote_key_val)
    #
    # records = ld.get_all_records(votes_conn,show_only=False)
    # print(records)

    # vote_for_block_key = "3d9423db02f5f8d56d2342316ae4a71fd78e8e45f99869a7c2cc8dc4126a5b57"

    vote_for_block_key_prefix = "c2"
    block_votes_dict = ld.get_val_prefix(votes_conn,vote_for_block_key_prefix)

    for vote_key,vote in block_votes_dict.items():
        print("vote_key={},\nvote={}\n".format(vote_key,vote))

    print("result[total={},prefix={}]".format(len(block_votes_dict),vote_for_block_key_prefix))

    total_records = ld.get_records_count(votes_conn)
    print("total_records is {}".format(total_records))

    ld.close(votes_conn)

