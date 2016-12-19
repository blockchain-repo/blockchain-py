"""Backend implementation for RethinkDB.

This module contains all the methods to store and retrieve data from RethinkDB.
"""

import rethinkdb as r

from extend.localdb.restore.rethinkdb_utils.utils import Connection


class RethinkDBBackend:

    def __init__(self, host=None, port=None, db=None):
        """Initialize a new RethinkDB Backend instance.

        Args:
            host (str): the host to connect to.
            port (int): the port to connect to.
            db (str): the name of the database to use.
        """

        self.read_mode = 'majority'
        self.durability = 'soft'
        self.connection = Connection(host=host, port=port, db=db)

    def get_transaction_from_block(self, transaction_id, block_id):
        """Get a transaction from a specific block.

        Args:
            transaction_id (str): the id of the transaction.
            block_id (str): the id of the block.

        Returns:
            The matching transaction.
        """
        return self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .get(block_id)
                .get_field('block')
                .get_field('transactions')
                .filter(lambda tx: tx['id'] == transaction_id))[0]

    def get_owned_ids(self, owner):
        """Retrieve a list of `txids` that can we used has inputs.

        Args:
            owner (str): base58 encoded public key.

        Returns:
            A cursor for the matching transactions.
        """

        # TODO: use index!
        return self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .concat_map(lambda doc: doc['block']['transactions'])
                .filter(lambda tx: tx['transaction']['conditions'].contains(
                    lambda c: c['owners_after'].contains(owner))))

    def get_votes_by_block_id(self, block_id):
        """Get all the votes casted for a specific block.

        Args:
            block_id (str): the block id to use.

        Returns:
            A cursor for the matching votes.
        """
        return self.connection.run(
                r.table('votes', read_mode=self.read_mode)
                .between([block_id, r.minval], [block_id, r.maxval], index='block_and_voter'))

    def get_votes_by_block_id_and_voter(self, block_id, node_pubkey):
        """Get all the votes casted for a specific block by a specific voter.

        Args:
            block_id (str): the block id to use.
            node_pubkey (str): base58 encoded public key

        Returns:
            A cursor for the matching votes.
        """
        return self.connection.run(
                r.table('votes', read_mode=self.read_mode)
                .get_all([block_id, node_pubkey], index='block_and_voter'))

    def write_block(self, block, durability='soft'):
        """Write a block to the bigchain table.

        Args:
            block (dict): the block to write.

        Returns:
            The database response.
        """
        return self.connection.run(
                r.table('bigchain')
                .insert(block, durability=durability))

    def has_transaction(self, transaction_id):
        """Check if a transaction exists in the bigchain table.

        Args:
            transaction_id (str): the id of the transaction to check.

        Returns:
            ``True`` if the transaction exists, ``False`` otherwise.
        """
        return bool(self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .get_all(transaction_id, index='transaction_id').count()))

    def count_blocks(self):
        """Count the number of blocks in the bigchain table.

        Returns:
            The number of blocks.
        """

        return self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .count())

    def count_votes(self):
        """Count the number of txs in the votes table.

        Returns:
            The number of txs.
        """

        return self.connection.run(
                r.table('votes', read_mode=self.read_mode)
                .count())

    def write_vote(self, vote):
        """Write a vote to the votes table.

        Args:
            vote (dict): the vote to write.

        Returns:
            The database response.
        """
        return self.connection.run(
                r.table('votes')
                .insert(vote))
