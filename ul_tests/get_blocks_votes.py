from bigchaindb import Bigchain
import rethinkdb as r

b = Bigchain()
block_list = b.get_BlockIdList(None, None)
block_list = list(block_list)

for block in block_list:
    block_voter = b.connection.run(r.table('bigchain').get(block))['block']['voters']
    votes = list(b.backend.get_votes_by_block_id(block))
    vote_cast = [vote['vote']['is_block_valid'] for vote in votes]
    block_status = b.block_election_status(block, block_voter)
    print(block, vote_cast, block_status, "\n", votes, "\n")
