import rethinkdb as r


def transaction_sum():
    stat_method = "half"
    vote_valid_num = 1

    begin_timestamp = "1506505226205"
    end_timestamp = "1506505238241"

    if stat_method == "half":
        vote_valid_num = int(vote_valid_num) / 2
    elif stat_method == "signal":
        vote_valid_num = 0

    tx_sum = 0

    conn = r.connect(db="bigchain")
    block_ids = r.table('votes').between(begin_timestamp, end_timestamp, index='vote_timestamp').get_field(
        'vote').group(
        'voting_for_block').count().run(conn)
    for block_id in block_ids:

        if block_ids[block_id] > int(vote_valid_num):
            block_txs = r.table('bigchain').get(block_id).get_field('block').get_field('transactions').count().run(conn)
            tx_sum = tx_sum + block_txs
    return tx_sum


if __name__ == '__main__':
    print(transaction_sum())
