from ul_tests.db.utils_rethinkdb import RethinkdbUtils


if __name__ == "__main__":

    rq = RethinkdbUtils()

    count_bigchain = rq.get_counts("bigchain")

    count_votes = rq.get_counts("votes")

    count_bigchain_between = rq.get_counts_between(table='bigchain',prefix_index='block',index='timestamp')


    print("count_bigchain={},count_votes={},count_bigchain_between={}\n".format(count_bigchain,count_votes,count_bigchain_between))

    # id = "c2e2e2fef589d5ec89c78a42d803788b4e9ce71273a1af999a12dfc95192c844"
    # print("block with id {} ,details is:\n{}".format(id,rq.get('bigchain',id)))

    # print("block with id {} ,details is:\n{}".format(id,rq.get('bigchain',id)))
    # print("get all votes by timestamp order, result is:\n{}".format(rq.get_val_between(table='votes',prefix_index='vote',index='timestamp',limit=1000,show_only=True)))
    # print("get all votes by timestamp order, result is:\n{}".format(rq.get_val_between(table='bigchain',prefix_index='block',index='timestamp',limit=1000,show_only=True)))

    block_count,txs_count,block_txs_count_list = rq.get_txs_count(order_by=True)
    print("get_txs_count query result: block number={},total txs={},detail info:\n{}"
          .format(block_count,txs_count,block_txs_count_list))


    # block_votes = rq.get_block_votes(id="f8f02ed4ae0308c52787bfa7c25387f03a494e62e27be6b5bd8965481592ee88")
    # print(block_votes)

    block_count, blocks_votes_count, block_votes_count_list =  rq.get_blocks_votes_count(order_by=True)
    print("\nget_blocks_votes_count query result: block number={},total votes={},detail info:\n{}"
          .format(block_count,blocks_votes_count,block_votes_count_list))
