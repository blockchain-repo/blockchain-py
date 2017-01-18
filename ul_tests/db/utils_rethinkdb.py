
import rethinkdb as r
import bigchaindb
from bigchaindb import Bigchain

class RethinkdbUtils():

    def __init__(self):
        # you can switch the db by init the Bigchain(dbname=you_choose_dbname)
        self.read_mode = 'majority'
        self.durability = 'soft'
        self.bigchain = Bigchain()
        self.db = bigchaindb.config['database']['name']
        self.tables = ['bigchain','votes','backlog']
        self.prefix_index = None
        self.index = "timestamp"
        self.left_bound = "open"
        self.right_bound = "closed"
        self.limit = 100

    def get_counts(self,table):

        if table is None or table not in self.tables:
            return 0

        return self.bigchain.connection.run(
            r.table(table).count())

    def get_counts_between(self,table,index,start=None,end=None,left_bound=None,right_bound=None,
                           prefix_index=None,order_by=False):

        """get the records count under the conditions

        Args:
           table:
           index: secondary index
           start:
           end:
           left_bound: default will use the 'open'
           right_bound: default will use the 'closed'
           prefix_index: the index prefix ,ex vote_ for index vote_timestamp
           order_by: order the query
           limit: the query`s max count
        Return:

        """

        if table is None or table not in self.tables:
            return 0

        if start is None:
            start = r.minval

        if end is None:
            end = r.maxval

        if left_bound is None:
            left_bound = self.left_bound

        if right_bound is None:
            right_bound = self.right_bound

        if prefix_index is not None:
            index = prefix_index + "_" + index

        if order_by:
            return self.bigchain.connection.run(r.table(table).between(start,end,left_bound=left_bound,
                                                                       right_bound=right_bound,index=index).order_by(index=r.asc(index)).count())
        else:
            return self.bigchain.connection.run(r.table(table).between(start, end,left_bound=left_bound,
                                                                       right_bound=right_bound, index=index).count())

    def get_val_between(self, table, index, start=None, end=None, left_bound=None, right_bound=None,
                           prefix_index=None, order_by=False,limit=None,show_only=False):

        """get the records under the conditions

        Args:
            table:
            index: secondary index
            start:
            end:
            left_bound: default will use the 'open'
            right_bound: default will use the 'closed'
            prefix_index: the index prefix ,ex vote_ for index vote_timestamp
            order_by: order the query
            limit: the query`s max count
            only_show: if True, only stdout the result and return None, default will return the result only

        Return:

        """

        if table is None or table not in self.tables:
            return None

        if start is None:
            start = r.minval

        if end is None:
            end = r.maxval

        if left_bound is None:
            left_bound = self.left_bound

        if right_bound is None:
            right_bound = self.right_bound

        if prefix_index is not None:
            index = prefix_index + "_" + index

        if limit is None:
            limit = self.limit

        result = None
        if order_by:
            result = self.bigchain.connection.run(r.table(table).between(start, end,left_bound=left_bound,right_bound=right_bound,
                                                                       index=index).order_by( index=r.asc(index)).limit(limit))
        else:
            result = self.bigchain.connection.run(r.table(table).between(start, end,left_bound=left_bound,
                                                                       right_bound=right_bound, index=index).limit(limit))
        output = []

        if show_only:
            count = 0
            for item in result:
                count += 1
                print("The {}th is: {}".format(count,item))
            print("Total records count is: {}".format(count))
        else:
            for item in result:
                output.append(item)
        return output

    def get(self,table,key):
        """get the records with default key in table

       Args:
           table:
           key: default index or key
       Return:

       """

        if table is None or table not in self.tables:
            return None

        if key is None:
            return None

        return self.bigchain.connection.run(r.table(table).get(key))

    def get_txs_count(self,id=None,order_by=False):
        """get all the transactions count in block

        Args:
            id:block_id
            order_by:
        Return:
            block_count: the count of the blocks
            txs_count: the count of total txs count
            block_txs_count_list: {id:block_txs_count}
        """

        table = 'bigchain'
        block_count = 0
        txs_count = 0
        block_txs_count_list = []

        if id:
            block = self.bigchain.connection.run(r.table(table).get(id))
            block_count = 1
            txs_count = len(block['block']['transactions'])

        else:
            if order_by:
                index = "block_timestamp"
                blocks = self.bigchain.connection.run(r.table(table).order_by(index=r.asc(index)))
            else:
                blocks = self.bigchain.connection.run(r.table(table))

            for block in blocks:
                block_count += 1
                block_id = block['id']
                block_txs_count = len(block['block']['transactions'])
                block_txs_count_dict = dict()
                block_txs_count_dict[block_id] = block_txs_count
                block_txs_count_list.append(block_txs_count_dict)
                txs_count += block_txs_count
                del block_txs_count_dict
        return block_count,txs_count,block_txs_count_list

    def get_votes_by_block_id(self, block_id):
        """Get all the votes casted for a specific block.

        Args:
            block_id (str): the block id to use.

        Returns:
            A cursor for the matching votes.
        """
        return self.bigchain.connection.run(
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
        return self.bigchain.connection.run(
            r.table('votes', read_mode=self.read_mode)
                .get_all([block_id, node_pubkey], index='block_and_voter'))

    def get_block_votes(self,id,order_by=False):
        """get all the votes for the special block or all blocks

        Args:
            id:block_id
            order_by:
        Return:
            A cursor for the matching votes.
        """
        if order_by:
            return self.bigchain.connection.run(r.table('votes', read_mode=self.read_mode).filter(
                r.row['vote']['voting_for_block'] == id).order_by(index=r.asc("vote_timestamp")))
        else:
            return self.bigchain.connection.run(r.table('votes',read_mode=self.read_mode).filter(
                r.row['vote']['voting_for_block'] == id))

    def get_blocks_votes_count(self,id=None,order_by=False):
        """get all the votes for the special block or all blocks

        Args:
            id:block_id
            order_by:
        Return:
            A cursor for the matching votes.
        """
        if order_by:
            if id:
                blocks = self.bigchain.connection.run(r.table('bigchain').ge(id))
            else:
                blocks = self.bigchain.connection.run(r.table('bigchain').order_by(index=r.asc("block_timestamp")))
        else:
            if id:
                blocks = self.bigchain.connection.run(r.table('bigchain').get(id))
            else:
                blocks = self.bigchain.connection.run(r.table('bigchain'))

        blocks_votes_count = 0
        block_votes_count_list = []
        block_count = 0
        for block in blocks:

            block_id = block['id']
            block_count += 1

            # block_votes_count = self.bigchain.connection.run(r.table('votes', read_mode=self.read_mode).filter(
            #     r.row['vote']['voting_for_block'] == block_id).count())

            block_votes_count = self.bigchain.connection.run(
                r.table('votes', read_mode=self.read_mode)
                    .between([block_id, r.minval], [block_id, r.maxval], index='block_and_voter').count())

            block_votes_count_dict = dict()
            block_votes_count_dict[block_id] = block_votes_count
            block_votes_count_list.append(block_votes_count_dict)
            blocks_votes_count += block_votes_count
            del block_votes_count_dict

        return block_count,blocks_votes_count,block_votes_count_list