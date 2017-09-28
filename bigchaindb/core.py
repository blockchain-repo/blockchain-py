import random
import math
import collections
from time import time, mktime, strptime
import requests
import json
from itertools import compress
from bigchaindb.common import crypto, exceptions
from bigchaindb.common.util import gen_timestamp, serialize
from bigchaindb.common.transaction import TransactionLink, Asset

import bigchaindb

from bigchaindb.db.utils import Connection, get_backend
from bigchaindb import config_utils, util
from bigchaindb.consensus import BaseConsensusRules
from bigchaindb.models import Block, Transaction


class Bigchain(object):
    """Bigchain API

    Create, read, sign, write transactions to the database
    """

    # return if a block has been voted invalid
    BLOCK_INVALID = 'invalid'
    # return if a block is valid, or tx is in valid block
    BLOCK_VALID = TX_VALID = 'valid'
    # return if block is undecided, or tx is in undecided block
    BLOCK_UNDECIDED = TX_UNDECIDED = 'undecided'
    # return if transaction is in backlog
    TX_IN_BACKLOG = 'backlog'

    def __init__(self, host=None, port=None, dbname=None, backend=None,
                 public_key=None, private_key=None, keyring=[],
                 backlog_reassign_delay=None):
        """Initialize the Bigchain instance

        A Bigchain instance has several configuration parameters (e.g. host).
        If a parameter value is passed as an argument to the Bigchain
        __init__ method, then that is the value it will have.
        Otherwise, the parameter value will come from an environment variable.
        If that environment variable isn't set, then the value
        will come from the local configuration file. And if that variable
        isn't in the local configuration file, then the parameter will have
        its default value (defined in bigchaindb.__init__).

        Args:
            host (str): hostname where RethinkDB is running.
            port (int): port in which RethinkDB is running (usually 28015).
            dbname (str): the name of the database to connect to (usually bigchain).
            backend (:class:`~bigchaindb.db.backends.rethinkdb.RehinkDBBackend`):
                the database backend to use.
            public_key (str): the base58 encoded public key for the ED25519 curve.
            private_key (str): the base58 encoded private key for the ED25519 curve.
            keyring (list[str]): list of base58 encoded public keys of the federation nodes.
        """

        config_utils.autoconfigure()
        self.host = host or bigchaindb.config['database']['host']
        self.port = port or bigchaindb.config['database']['port']
        self.dbname = dbname or bigchaindb.config['database']['name']
        self.backend = backend or get_backend(host, port, dbname)
        self.me = public_key or bigchaindb.config['keypair']['public']
        self.me_private = private_key or bigchaindb.config['keypair']['private']
        self.nodes_except_me = keyring or bigchaindb.config['keyring']
        self.backlog_reassign_delay = backlog_reassign_delay or bigchaindb.config['backlog_reassign_delay']
        self.order_api = '' or bigchaindb.config['order_api']
        self.consensus = BaseConsensusRules
        # change RethinkDB read mode to majority.  This ensures consistency in query results
        self.read_mode = 'majority'
        self.split_backlog = False or bigchaindb.config['argument_config']['split_backlog']
        if not self.me or not self.me_private:
            raise exceptions.KeypairNotFoundException()

        self.connection = Connection(host=self.host, port=self.port, db=self.dbname)
        self.nodelist = self.nodes_except_me.copy()
        self.nodelist.append(self.me)
        self.nodelist.sort()

    def write_transaction(self, signed_transaction, durability='soft'):
        """Write the transaction to bigchain.

        When first writing a transaction to the bigchain the transaction will be kept in a backlog until
        it has been validated by the nodes of the federation.

        Args:
            signed_transaction (Transaction): transaction with the `signature` included.

        Returns:
            dict: database response
        """
        signed_transaction = signed_transaction.to_dict()

        # we will assign this transaction to `one` node. This way we make sure that there are no duplicate
        # transactions on the bigchain
        if self.nodes_except_me:
            assignee = random.choice(self.nodes_except_me)
        else:
            # I am the only node
            assignee = self.me

        signed_transaction.update({'assignee': assignee})
        signed_transaction.update({'assignment_timestamp': time()})
        signed_transaction.update({'assignee_isdeal': False})
        if self.split_backlog:
            # write to the backlog
            node_name = assignee[0:5]
            return self.backend.write_transaction_to_all(signed_transaction, node_name=node_name)
        return self.backend.write_transaction(signed_transaction)

    def reassign_transaction(self, transaction):
        """Assign a transaction to a new node

        Args:
            transaction (dict): assigned transaction

        Returns:
            dict: database response or None if no reassignment is possible
        """

        if self.nodes_except_me:
            try:
                federation_nodes = self.nodes_except_me + [self.me]
                index_current_assignee = federation_nodes.index(transaction['assignee'])
                new_assignee = random.choice(federation_nodes[:index_current_assignee] +
                                             federation_nodes[index_current_assignee + 1:])
            except ValueError:
                # current assignee not in federation
                new_assignee = random.choice(self.nodes_except_me)

        else:
            # There is no other node to assign to
            new_assignee = self.me
        # print("reassign:"+str(transaction['id']))
        if self.split_backlog:
            node_name = self.me[0:5]
        else:
            node_name = ''

        return self.backend.update_transaction(
            transaction['id'],
            {'assignee': new_assignee, 'assignment_timestamp': time(), 'assignee_isdeal': False}, node_name=node_name)

    def delete_transaction(self, *transaction_id):
        """Delete a transaction from the backlog.

        Args:
            *transaction_id (str): the transaction(s) to delete

        Returns:
            The database response.
        """
        if self.split_backlog:
            node_name = self.me[0:5]
        else:
            node_name = ''
        return self.backend.delete_transaction(*transaction_id, node_name=node_name)

    def get_stale_transactions(self):
        """Get a cursor of stale transactions.

        Transactions are considered stale if they have been assigned a node, but are still in the
        backlog after some amount of time specified in the configuration
        """

        return self.backend.get_stale_transactions(self.backlog_reassign_delay)

    def validate_transaction(self, transaction):
        """Validate a transaction.

        Args:
            transaction (Transaction): transaction to validate.

        Returns:
            The transaction if the transaction is valid else it raises an
            exception describing the reason why the transaction is invalid.
        """

        return self.consensus.validate_transaction(self, transaction)

    def is_valid_transaction(self, transaction):
        """Check whether a transaction is valid or invalid.

        Similar to :meth:`~bigchaindb.Bigchain.validate_transaction`
        but never raises an exception. It returns :obj:`False` if
        the transaction is invalid.

        Args:
            transaction (:Class:`~bigchaindb.models.Transaction`): transaction
                to check.

        Returns:
            The :class:`~bigchaindb.models.Transaction` instance if valid,
            otherwise :obj:`False`.
        """

        try:
            return self.validate_transaction(transaction)
        except (ValueError, exceptions.OperationError, exceptions.TransactionDoesNotExist,
                exceptions.TransactionOwnerError, exceptions.DoubleSpend,
                exceptions.InvalidHash, exceptions.InvalidSignature,
                exceptions.FulfillmentNotInValidBlock):
            return False

    def get_transaction(self, txid, include_status=False):
        """Get the transaction with the specified `txid` (and optionally its status)

        This query begins by looking in the bigchain table for all blocks containing
        a transaction with the specified `txid`. If one of those blocks is valid, it
        returns the matching transaction from that block. Else if some of those
        blocks are undecided, it returns a matching transaction from one of them. If
        the transaction was found in invalid blocks only, or in no blocks, then this
        query looks for a matching transaction in the backlog table, and if it finds
        one there, it returns that.

        Args:
            txid (str): transaction id of the transaction to get
            include_status (bool): also return the status of the transaction
                                   the return value is then a tuple: (tx, status)

        Returns:
            A :class:`~.models.Transaction` instance if the transaction
            was found in a valid block, an undecided block, or the backlog table,
            otherwise ``None``.
            If :attr:`include_status` is ``True``, also returns the
            transaction's status if the transaction was found.
        """

        response, tx_status = None, None

        validity = self.get_blocks_status_containing_tx(txid)
        check_backlog = True

        if validity:
            # Disregard invalid blocks, and return if there are no valid or undecided blocks
            validity = {_id: status for _id, status in validity.items()
                        if status != Bigchain.BLOCK_INVALID}
            if validity:

                # The transaction _was_ found in an undecided or valid block,
                # so there's no need to look in the backlog table
                check_backlog = False

                tx_status = self.TX_UNDECIDED
                # If the transaction is in a valid or any undecided block, return it. Does not check
                # if transactions in undecided blocks are consistent, but selects the valid block
                # before undecided ones
                for target_block_id in validity:
                    if validity[target_block_id] == Bigchain.BLOCK_VALID:
                        tx_status = self.TX_VALID
                        break

                # Query the transaction in the target block and return
                response = self.backend.get_transaction_from_block(txid, target_block_id)

        if check_backlog:
            response = self.backend.get_transaction_from_backlog(txid)

            if response:
                tx_status = self.TX_IN_BACKLOG

        if response:
            response = Transaction.from_dict(response)

        if include_status:
            return response, tx_status
        else:
            return response

    def get_status(self, txid):
        """Retrieve the status of a transaction with `txid` from bigchain.

        Args:
            txid (str): transaction id of the transaction to query

        Returns:
            (string): transaction status ('valid', 'undecided',
            or 'backlog'). If no transaction with that `txid` was found it
            returns `None`
        """
        _, status = self.get_transaction(txid, include_status=True)
        return status

    def get_blocks_status_containing_tx(self, txid):
        """Retrieve block ids and statuses related to a transaction

        Transactions may occur in multiple blocks, but no more than one valid block.

        Args:
            txid (str): transaction id of the transaction to query

        Returns:
            A dict of blocks containing the transaction,
            e.g. {block_id_1: 'valid', block_id_2: 'invalid' ...}, or None
        """

        # First, get information on all blocks which contain this transaction
        blocks = self.backend.get_blocks_status_from_transaction(txid)
        if blocks:
            # Determine the election status of each block
            validity = {
                block['id']: self.block_election_status(
                    block['id'],
                    block['block']['voters']
                ) for block in blocks
            }

            # NOTE: If there are multiple valid blocks with this transaction,
            # something has gone wrong
            if list(validity.values()).count(Bigchain.BLOCK_VALID) > 1:
                block_ids = str([block for block in validity
                                 if validity[block] == Bigchain.BLOCK_VALID])
                raise exceptions.DoubleSpend('Transaction {tx} is present in '
                                             'multiple valid blocks: '
                                             '{block_ids}'
                                             .format(tx=txid,
                                                     block_ids=block_ids))

            return validity

        else:
            return None

    def get_tx_by_metadata_id(self, metadata_id):
        """Retrieves transactions related to a metadata.

        When creating a transaction one of the optional arguments is the `metadata`. The metadata is a generic
        dict that contains extra information that can be appended to the transaction.

        To make it easy to query the bigchain for that particular metadata we create a UUID for the metadata and
        store it with the transaction.

        Args:
            metadata_id (str): the id for this particular metadata.

        Returns:
            A list of transactions containing that metadata. If no transaction exists with that metadata it
            returns an empty list `[]`
        """
        cursor = self.backend.get_transactions_by_metadata_id(metadata_id)
        return [Transaction.from_dict(tx) for tx in cursor]

    def get_txs_by_asset_id(self, asset_id):
        """Retrieves transactions related to a particular asset.

        A digital asset in bigchaindb is identified by an uuid. This allows us to query all the transactions
        related to a particular digital asset, knowing the id.

        Args:
            asset_id (str): the id for this particular metadata.

        Returns:
            A list of transactions containing related to the asset. If no transaction exists for that asset it
            returns an empty list `[]`
        """

        cursor = self.backend.get_transactions_by_asset_id(asset_id)
        return [Transaction.from_dict(tx) for tx in cursor]

    def get_spent(self, txid, cid):
        """Check if a `txid` was already used as an input.

        A transaction can be used as an input for another transaction. Bigchain needs to make sure that a
        given `txid` is only used once.

        Args:
            txid (str): The id of the transaction
            cid (num): the index of the condition in the respective transaction

        Returns:
            The transaction (Transaction) that used the `txid` as an input else
            `None`
        """
        # checks if an input was already spent
        # checks if the bigchain has any transaction with input {'txid': ..., 'cid': ...}
        transactions = list(self.backend.get_spent(txid, cid))

        # a transaction_id should have been spent at most one time
        if transactions:
            # determine if these valid transactions appear in more than one valid block
            num_valid_transactions = 0
            for transaction in transactions:
                # ignore invalid blocks
                # FIXME: Isn't there a faster solution than doing I/O again?
                if self.get_transaction(transaction['id']):
                    num_valid_transactions += 1
                if num_valid_transactions > 1:
                    raise exceptions.DoubleSpend(
                        '`{}` was spent more then once. There is a problem with the chain'.format(
                            txid))

            if num_valid_transactions:
                return Transaction.from_dict(transactions[0])
            else:
                # all queried transactions were invalid
                return None
        else:
            return None

    def get_owned_ids(self, owner):
        """Retrieve a list of `txid`s that can be used as inputs.

        Args:
            owner (str): base58 encoded public key.

        Returns:
            :obj:`list` of TransactionLink: list of `txid`s and `cid`s
            pointing to another transaction's condition
        """

        # get all transactions in which owner is in the `owners_after` list
        response = self.backend.get_owned_ids(owner)
        owned = []

        for tx in response:
            # disregard transactions from invalid blocks
            validity = self.get_blocks_status_containing_tx(tx['id'])
            if Bigchain.BLOCK_VALID not in validity.values():
                if Bigchain.BLOCK_UNDECIDED not in validity.values():
                    continue

            # NOTE: It's OK to not serialize the transaction here, as we do not
            # use it after the execution of this function.
            # a transaction can contain multiple outputs (conditions) so we need to iterate over all of them
            # to get a list of outputs available to spend
            for index, cond in enumerate(tx['transaction']['conditions']):
                # for simple signature conditions there are no subfulfillments
                # check if the owner is in the condition `owners_after`
                if len(cond['owners_after']) == 1:
                    if cond['condition']['details']['public_key'] == owner:
                        tx_link = TransactionLink(tx['id'], index)
                else:
                    # for transactions with multiple `owners_after` there will be several subfulfillments nested
                    # in the condition. We need to iterate the subfulfillments to make sure there is a
                    # subfulfillment for `owner`
                    if util.condition_details_has_owner(cond['condition']['details'], owner):
                        tx_link = TransactionLink(tx['id'], index)
                # check if input was already spent
                if not self.get_spent(tx_link.txid, tx_link.cid):
                    owned.append(tx_link)

        return owned

    def create_block(self, validated_transactions):
        """Creates a block given a list of `validated_transactions`.

        Note that this method does not validate the transactions. Transactions
        should be validated before calling create_block.

        Args:
            validated_transactions (list(Transaction)): list of validated
                                                        transactions.

        Returns:
            Block: created block.
        """
        # Prevent the creation of empty blocks
        if len(validated_transactions) == 0:
            raise exceptions.OperationError('Empty block creation is not '
                                            'allowed')

        voters = self.nodes_except_me + [self.me]
        block = Block(validated_transactions, self.me, gen_timestamp(), voters)
        block = block.sign(self.me_private)

        return block

    # TODO: check that the votings structure is correctly constructed
    def validate_block(self, block):
        """Validate a block.

        Args:
            block (Block): block to validate.

        Returns:
            The block if the block is valid else it raises and exception
            describing the reason why the block is invalid.
        """
        return self.consensus.validate_block(self, block)

    def has_previous_vote(self, block_id, voters):
        """Check for previous votes from this node

        Args:
            block_id (str): the id of the block to check
            voters (list(str)): the voters of the block to check

        Returns:
            bool: :const:`True` if this block already has a
            valid vote from this node, :const:`False` otherwise.

        Raises:
            ImproperVoteError: If there is already a vote,
                but the vote is invalid.

        """
        votes = list(self.backend.get_votes_by_block_id_and_voter(block_id, self.me))

        if len(votes) > 1:
            raise exceptions.MultipleVotesError('Block {block_id} has {n_votes} votes from public key {me}'
                                                .format(block_id=block_id, n_votes=str(len(votes)), me=self.me))
        has_previous_vote = False
        if votes:
            if util.verify_vote_signature(voters, votes[0]):
                has_previous_vote = True
            else:
                raise exceptions.ImproperVoteError('Block {block_id} already has an incorrectly signed vote '
                                                   'from public key {me}'.format(block_id=block_id, me=self.me))

        return has_previous_vote

    def write_block(self, block, durability='soft'):
        """Write a block to bigchain.

        Args:
            block (Block): block to write to bigchain.
        """

        return self.backend.write_block(block.to_str(), durability=durability)

    def transaction_exists(self, transaction_id):
        return self.backend.has_transaction(transaction_id)

    def transactions_list_exists(self, transactions):
        return self.backend.has_transactions_list(transactions)

    def prepare_genesis_block(self):
        """Prepare a genesis block."""

        metadata = {'message': 'Hello World from the BigchainDB'}
        transaction = Transaction.create([self.me], [([self.me], 1)],
                                         metadata=metadata)

        # NOTE: The transaction model doesn't expose an API to generate a
        #       GENESIS transaction, as this is literally the only usage.
        transaction.operation = 'GENESIS'
        transaction = transaction.sign([self.me_private])

        # create the block
        return self.create_block([transaction])

    def create_genesis_block(self):
        """Create the genesis block

        Block created when bigchain is first initialized. This method is not atomic, there might be concurrency
        problems if multiple instances try to write the genesis block when the BigchainDB Federation is started,
        but it's a highly unlikely scenario.
        """

        # 1. create one transaction
        # 2. create the block with one transaction
        # 3. write the block to the bigchain

        blocks_count = self.backend.count_blocks()

        if blocks_count:
            raise exceptions.GenesisBlockAlreadyExistsError('Cannot create the Genesis block')

        block = self.prepare_genesis_block()
        self.write_block(block, durability='hard')

        return block

    def vote(self, block_id, previous_block_id, decision, invalid_reason=None):
        """Create a signed vote for a block given the
        :attr:`previous_block_id` and the :attr:`decision` (valid/invalid).

        Args:
            block_id (str): The id of the block to vote on.
            previous_block_id (str): The id of the previous block.
            decision (bool): Whether the block is valid or invalid.
            invalid_reason (Optional[str]): Reason the block is invalid
        """

        if block_id == previous_block_id:
            raise exceptions.CyclicBlockchainError()

        vote = {
            'voting_for_block': block_id,
            'previous_block': previous_block_id,
            'is_block_valid': decision,
            'invalid_reason': invalid_reason,
            'timestamp': gen_timestamp()
        }

        vote_data = serialize(vote)
        signature = crypto.SigningKey(self.me_private).sign(vote_data.encode())

        vote_signed = {
            'node_pubkey': self.me,
            'signature': signature,
            'vote': vote
        }

        return vote_signed

    def write_vote(self, vote):
        """Write the vote to the database."""
        return self.backend.write_vote(vote)

    def get_last_voted_block(self):
        """Returns the last block that this node voted on."""

        return Block.from_dict(self.backend.get_last_voted_block(self.me))

    def get_unvoted_blocks(self):
        """Return all the blocks that have not been voted on by this node.

        Returns:
            :obj:`list` of :obj:`dict`: a list of unvoted blocks
        """

        # XXX: should this return instaces of Block?
        return self.backend.get_unvoted_blocks(self.me)

    def block_election_status(self, block_id, voters):
        """Tally the votes on a block, and return the status: valid, invalid, or undecided."""

        votes = list(self.backend.get_votes_by_block_id(block_id))
        n_voters = len(voters)

        voter_counts = collections.Counter([vote['node_pubkey'] for vote in votes])
        for node in voter_counts:
            if voter_counts[node] > 1:
                raise exceptions.MultipleVotesError(
                    'Block {block_id} has multiple votes ({n_votes}) from voting node {node_id}'
                        .format(block_id=block_id, n_votes=str(voter_counts[node]), node_id=node))

        if len(votes) > n_voters:
            raise exceptions.MultipleVotesError('Block {block_id} has {n_votes} votes cast, but only {n_voters} voters'
                                                .format(block_id=block_id, n_votes=str(len(votes)),
                                                        n_voters=str(n_voters)))

        # vote_cast is the list of votes e.g. [True, True, False]
        vote_cast = [vote['vote']['is_block_valid'] for vote in votes]
        # prev_block are the ids of the nominal prev blocks e.g.
        # ['block1_id', 'block1_id', 'block2_id']
        prev_block = [vote['vote']['previous_block'] for vote in votes]
        # vote_validity checks whether a vote is valid
        # or invalid, e.g. [False, True, True]
        vote_validity = [self.consensus.verify_vote_signature(voters, vote) for vote in votes]

        # element-wise product of stated vote and validity of vote
        # vote_cast = [True, True, False] and
        # vote_validity = [False, True, True] gives
        # [True, False]
        # Only the correctly signed votes are tallied.
        vote_list = list(compress(vote_cast, vote_validity))

        # Total the votes. Here, valid and invalid refer
        # to the vote cast, not whether the vote itself
        # is valid or invalid.
        n_valid_votes = sum(vote_list)
        n_invalid_votes = len(vote_cast) - n_valid_votes

        # The use of ceiling and floor is to account for the case of an
        # even number of voters where half the voters have voted 'invalid'
        # and half 'valid'. In this case, the block should be marked invalid
        # to avoid a tie. In the case of an odd number of voters this is not
        # relevant, since one side must be a majority.
        if n_invalid_votes >= math.ceil(n_voters / 2):
            return Bigchain.BLOCK_INVALID
        elif n_valid_votes > math.floor(n_voters / 2):
            # The block could be valid, but we still need to check if votes
            # agree on the previous block.
            #
            # First, only consider blocks with legitimate votes
            prev_block_list = list(compress(prev_block, vote_validity))
            # Next, only consider the blocks with 'yes' votes
            prev_block_valid_list = list(compress(prev_block_list, vote_list))
            counts = collections.Counter(prev_block_valid_list)
            # Make sure the majority vote agrees on previous node.
            # The majority vote must be the most common, by definition.
            # If it's not, there is no majority agreement on the previous
            # block.
            if counts.most_common()[0][1] > math.floor(n_voters / 2):
                return Bigchain.BLOCK_VALID
            else:
                if len(votes) < n_voters:
                    return Bigchain.BLOCK_UNDECIDED
                else:
                    return Bigchain.BLOCK_INVALID
        else:
            return Bigchain.BLOCK_UNDECIDED

    # zy@secn
    def get_backlog_tx_number(self):
        return self.backend.count_backlog_txs()

    # @author lz  for reassignee
    def init_heartbeat_data(self):
        self.backend.delete_heartbeat(self.me)
        data = {'node_publickey': self.me, 'timestamp': time()}
        return self.backend.init_heartbeat(data)

    def init_reassignnode_data(self):
        if not self.backend.isReassignnodeExist():
            data = {"nodeid": 0, 'node_publickey': self.nodelist[0], 'timestamp': time()}
            self.backend.init_reassignnode(data)

    def updateHeartbeat(self, time):
        return self.backend.updateHeartbeat(self.me, time)

    def getAssigneekey(self):
        nodeid = self.backend.getAssigneekey().next()['nodeid']
        assigneekey = self.backend.getAssigneekey().next()['node_publickey']
        return nodeid, assigneekey

    def updateAssigneebeat(self, assigneekey, time):
        return self.backend.updateAssigneebeat(assigneekey, time)

    def is_assignee_alive(self, assigneekey, timeout):
        try:
            timestamp = self.backend.is_assignee_alive(assigneekey).next()['timestamp']
        except:
            timestamp = 0.0
        if (time() - timestamp) > timeout:
            return False
        return True

    def is_node_alive(self, txpublickey, timeout):
        try:
            timestamp = self.backend.is_node_alive(txpublickey).next()['timestamp']
        except:
            timestamp = 0.0

        if (time() - timestamp) > timeout:
            return False
        return True

    def update_assign_node(self, updateid, next_assign_node):
        return self.backend.update_assign_node(updateid, next_assign_node)

    # @author lz for rewrite
    def insertRewrite(self, data):
        return self.backend.insertRewrite(data)

    def selectFromWrite(self, id):
        return self.backend.isBlockRewrited(id)

    ##############################
    ####  for unichian api   #####
    ##############################
    def get_txCreateAvgTimeByRange(self, begintime, endtime):
        status = True
        if endtime > gen_timestamp() or endtime < begintime:
            status = False
            return 0, status
        avgtime, ret = self.backend.get_transaction_createavgtime_by_range(begintime, endtime)
        if not ret:
            status = False
            return 0, status
        return avgtime, status

    def get_blockCreateAvgTimeByRange(self, begintime, endtime):
        status = True
        if endtime > gen_timestamp() or endtime < begintime:
            status = False
            return 0, status
        avgtime, ret = self.backend.get_block_createavgtime_by_range(begintime, endtime)
        if not ret:
            status = False
            return 0, status
        return avgtime, status

    def get_voteTimeByBlockID(self, block_id):
        status = True
        if not self.backend.get_block_by_id(block_id):
            return 0, status
        avgtime, ret = self.backend.get_vote_time_by_blockid(block_id)
        if not ret:
            status = False
            return 0, status
        return avgtime, status

    def get_voteAvgTimeByRange(self, begintime, endtime):
        status = True
        if endtime > gen_timestamp() or endtime < begintime:
            status = False
            return 0, status
        avgtime, ret = self.backend.get_vote_avgtime_by_range(begintime, endtime)
        if not ret:
            status = False
            return 0, status
        return avgtime, status

    # @author lz For commen-api
    def get_txNumber(self, block_id=None):
        if block_id == None:
            return self.backend.get_txNumber()
        else:
            return self.backend.get_txNumberById(block_id)

    def get_BlockNumber(self):
        return self.backend.get_BlockNumber()

    def get_invalidBlockIdList(self, startTime=None, endTime=None):
        if startTime is None and endTime is None:
            return self.backend.get_allInvalidBlock()
        else:
            return self.backend.get_invalidBlockByTime(startTime, endTime)

    def get_allInvalidBlock_number(self, startTime=None, endTime=None):
        return self.backend.get_allInvalidBlock_number()

    def get_BlockIdList(self, startTime, endTime):
        if startTime is None and endTime is None:
            blockCount = self.backend.get_BlockNumber()
            if blockCount > 1000:
                return self.backend.get_BlockIdList(limit=1000)
            return self.backend.get_BlockIdList()
        else:
            blockCount = self.backend.get_BlockNumber(startTime=startTime, endTime=endTime)
            if blockCount > 1000:
                return self.backend.get_BlockIdList(startTime=startTime, endTime=endTime, limit=1000)
            return self.backend.get_BlockIdList(startTime=startTime, endTime=endTime)

    def get_TxIdByTime(self, startTime, endTime):
        txCount = self.backend.get_txNumber(startTime=startTime, endTime=endTime)
        if txCount > 2000:
            return self.backend.get_txIdList(startTime=startTime, endTime=endTime, limit=2000)
        return self.backend.get_txIdList(startTime=startTime, endTime=endTime)

    def get_txNumberOfAllBlock(self):
        blockCount = self.backend.get_BlockNumber()
        if blockCount > 1000:
            # 输出1000条数据
            print("The resule is too big,onlg shows the recent 1000 records")
            return self.backend.get_txNumberOfEachBlock(limit=1000)
        else:
            return self.backend.get_txNumberOfEachBlock()
            # 全部输出

    def get_allPublicKey(self):
        self.nodelist = self.nodes_except_me.copy()
        self.nodelist.append(self.me)
        return self.nodelist

    def get_block(self, block_id, include_status=False):
        block = self.backend.get_block(block_id)
        return block

    def get_tx_by_id(self, tx_id):
        return self.backend.get_tx_by_id(tx_id)

    def get_transaction_no_valid(self, tx_id):
        return self.backend.get_transaction_no_valid(tx_id)

    def get_outputs_not_include_freeze(self, owner):
        """Retrieve a list of links to transaction outputs for a given public
                   key.

                Args:
                    owner (str): base58 encoded public key.

                Returns:
                    :obj:`list` of TransactionLink: list of ``txid`` s and ``output`` s
                    pointing to another transaction's condition
                """
        # get all transactions in which owner is in the `owners_after` list
        response = self.backend.get_owned_ids(owner)
        links = []
        for tx in response:
            # disregard transactions from invalid blocks
            validity = self.get_blocks_status_containing_tx(tx['id'])
            if Bigchain.BLOCK_VALID not in validity.values():
                continue

                # if Bigchain.BLOCK_UNDECIDED not in validity.values():
                #     continue
            # if
            # NOTE: It's OK to not serialize the transaction here, as we do not
            # use it after the execution of this function.
            # a transaction can contain multiple outputs so we need to iterate over all of them
            # to get a list of outputs available to spend
            for index, output in enumerate(tx['transaction']['conditions']):
                # for simple signature conditions there are no subfulfillments
                # check if the owner is in the condition `owners_after`
                if output['isfreeze']:
                    continue
                details = output['condition']['details']
                amount = output['amount']
                merged = {'details': details, 'amount': amount}

                if len(output['owners_after']) == 1:
                    if output['condition']['details']['public_key'] == owner:
                        tx_link = TransactionLink(tx['id'], index)
                        links.append(dict(tx_link.to_dict(), **merged))

                else:
                    # for transactions with multiple `public_keys` there will be several subfulfillments nested
                    # in the condition. We need to iterate the subfulfillments to make sure there is a
                    # subfulfillment for `owner`
                    if util.condition_details_has_owner(output['condition']['details'], owner):
                        tx_link = TransactionLink(tx['id'], index)
                        links.append(dict(tx_link.to_dict(), **merged))

                        # linksAmount.append(amount)

        return links

    def only_get_freeze_outputs(self, owner):
        """Retrieve a list of links to transaction outputs for a given public
                   key.

                Args:
                    owner (str): base58 encoded public key.

                Returns:
                    :obj:`list` of TransactionLink: list of ``txid`` s and ``output`` s
                    pointing to another transaction's condition
                """
        # get all transactions in which owner is in the `owners_after` list
        response = self.backend.get_owned_ids(owner)
        links = []
        for tx in response:
            # disregard transactions from invalid blocks
            validity = self.get_blocks_status_containing_tx(tx['id'])
            if Bigchain.BLOCK_VALID not in validity.values():
                if Bigchain.BLOCK_UNDECIDED not in validity.values():
                    continue

            # NOTE: It's OK to not serialize the transaction here, as we do not
            # use it after the execution of this function.
            # a transaction can contain multiple outputs so we need to iterate over all of them
            # to get a list of outputs available to spend
            for index, output in enumerate(tx['transaction']['conditions']):
                # for simple signature conditions there are no subfulfillments
                # check if the owner is in the condition `owners_after`
                # print(output)
                if not output['isfreeze']:
                    continue
                details = output['condition']['details']
                amount = output['amount']
                merged = {'details': details, 'amount': amount}

                if len(output['owners_after']) == 1:
                    if output['condition']['details']['public_key'] == owner:
                        tx_link = TransactionLink(tx['id'], index)
                        links.append(dict(tx_link.to_dict(), **merged))

                else:
                    # for transactions with multiple `public_keys` there will be several subfulfillments nested
                    # in the condition. We need to iterate the subfulfillments to make sure there is a
                    # subfulfillment for `owner`
                    if util.condition_details_has_owner(output['condition']['details'], owner):
                        tx_link = TransactionLink(tx['id'], index)
                        links.append(dict(tx_link.to_dict(), **merged))

                        # linksAmount.append(amount)

        return links

    def get_outputs_include_freeze(self, owner):
        """Retrieve a list of links to transaction outputs for a given public
           key.

        Args:
            owner (str): base58 encoded public key.

        Returns:
            :obj:`list` of TransactionLink: list of ``txid`` s and ``output`` s
            pointing to another transaction's condition
        """
        # get all transactions in which owner is in the `owners_after` list
        response = self.backend.get_owned_ids(owner)

        links = []
        for tx in response:
            # disregard transactions from invalid blocks
            validity = self.get_blocks_status_containing_tx(tx['id'])
            if Bigchain.BLOCK_VALID not in validity.values():
                if Bigchain.BLOCK_UNDECIDED not in validity.values():
                    continue

            # NOTE: It's OK to not serialize the transaction here, as we do not
            # use it after the execution of this function.
            # a transaction can contain multiple outputs so we need to iterate over all of them
            # to get a list of outputs available to spend
            for index, output in enumerate(tx['transaction']['conditions']):
                # for simple signature conditions there are no subfulfillments
                # check if the owner is in the condition `owners_after`
                details = output['condition']['details']
                amount = output['amount']
                merged = {'details': details, 'amount': amount}

                if len(output['owners_after']) == 1:
                    if output['condition']['details']['public_key'] == owner:
                        tx_link = TransactionLink(tx['id'], index)
                        links.append(dict(tx_link.to_dict(), **merged))

                else:
                    # for transactions with multiple `public_keys` there will be several subfulfillments nested
                    # in the condition. We need to iterate the subfulfillments to make sure there is a
                    # subfulfillment for `owner`
                    if util.condition_details_has_owner(output['condition']['details'], owner):
                        tx_link = TransactionLink(tx['id'], index)
                        links.append(dict(tx_link.to_dict(), **merged))

                        # linksAmount.append(amount)

        return links

    def get_outputs_freeze(self, owner, contract_id, task_id, task_num):
        """Retrieve a list of links to transaction outputs for a given public
                   key.

                Args:
                    owner (str): base58 encoded public key.

                Returns:
                    :obj:`list` of TransactionLink: list of ``txid`` s and ``output`` s
                    pointing to another transaction's condition
                """
        # get all transactions in which owner is in the `owners_after` list
        response = self.backend.get_owned_ids_by_task(owner, contract_id, task_id, task_num)
        # print("1---",response)
        links = []
        for tx in response:
            # print("2---")
            # disregard transactions from invalid blocks
            validity = self.get_blocks_status_containing_tx(tx['id'])
            # print("3---",validity)
            if Bigchain.BLOCK_VALID not in validity.values():
                if Bigchain.BLOCK_UNDECIDED not in validity.values():
                    continue
            # print("4---")
            # NOTE: It's OK to not serialize the transaction here, as we do not
            # use it after the execution of this function.
            # a transaction can contain multiple outputs so we need to iterate over all of them
            # to get a list of outputs available to spend
            for index, output in enumerate(tx['transaction']['conditions']):
                # for simple signature conditions there are no subfulfillments
                # check if the owner is in the condition `owners_after`
                # print(index)
                if not output['isfreeze']:
                    continue

                details = output['condition']['details']
                amount = output['amount']
                merged = {'details': details, 'amount': amount}

                if len(output['owners_after']) == 1:
                    if output['condition']['details']['public_key'] == owner:
                        tx_link = TransactionLink(tx['id'], index)
                        links.append(dict(tx_link.to_dict(), **merged))

                else:
                    # for transactions with multiple `public_keys` there will be several subfulfillments nested
                    # in the condition. We need to iterate the subfulfillments to make sure there is a
                    # subfulfillment for `owner`
                    if util.condition_details_has_owner(output['condition']['details'], owner):
                        tx_link = TransactionLink(tx['id'], index)
                        links.append(dict(tx_link.to_dict(), **merged))

                        # linksAmount.append(amount)

        return links

    def get_outputs_freeze_by_id(self, transaction_id):
        """Retrieve a list of links to transaction outputs for a given public
                   key.

                Args:
                    owner (str): base58 encoded public key.

                Returns:
                    :obj:`list` of TransactionLink: list of ``txid`` s and ``output`` s
                    pointing to another transaction's condition
                """
        # get all transactions in which owner is in the `owners_after` list
        response = self.backend.get_owned_ids_by_id(transaction_id)
        # print("1---",response)
        links = []
        for tx in response:
            # print("2---")
            # disregard transactions from invalid blocks
            validity = self.get_blocks_status_containing_tx(tx['id'])
            # print("3---",validity)
            if Bigchain.BLOCK_VALID not in validity.values():
                if Bigchain.BLOCK_UNDECIDED not in validity.values():
                    continue
            # print("4---")
            # NOTE: It's OK to not serialize the transaction here, as we do not
            # use it after the execution of this function.
            # a transaction can contain multiple outputs so we need to iterate over all of them
            # to get a list of outputs available to spend
            for index, output in enumerate(tx['transaction']['conditions']):
                # for simple signature conditions there are no subfulfillments
                # check if the owner is in the condition `owners_after`
                # print(index)
                if not output['isfreeze']:
                    continue

                details = output['condition']['details']
                amount = output['amount']
                merged = {'details': details, 'amount': amount}

                tx_link = TransactionLink(tx['id'], index)
                links.append(dict(tx_link.to_dict(), **merged))

        return links

    def filter_unspent(self, outputs):
        outputs = [o for o in outputs
                   if not self.get_spent(o['txid'], o['cid'])]
        return outputs

    def is_asset_transfer(self, txid, cid):
        transactions = list(self.backend.get_spent(txid, cid))
        if transactions:
            num_valid_transactions = 0
            for transaction in transactions:
                if self.get_transaction(transaction['id']):
                    num_valid_transactions += 1
                if num_valid_transactions > 1:
                    raise exceptions.DoubleSpend(
                        '`{}` was spent more then once. There is a problem with the chain'.format(txid))
            if num_valid_transactions:
                # only one
                txDict = transactions[0]
                tx = Transaction.from_dict(txDict)
                con = tx.conditions
                ful = tx.fulfillments
                if len(ful) > 0 and len(con) > 0:
                    ownerbefore = transactions[0]["transaction"]["fulfillments"][0]["owners_before"][0]
                    ownerafter = transactions[0]["transaction"]["conditions"][0]["owners_after"][0]
                    # print(ownerbefore,ownerafter)
                    # print(ownerbefore == ownerafter)
                    if ownerbefore != ownerafter:
                        return True
                    return False
                else:
                    return True
        return False

    # todo check the output is transfer or unfreeze
    def check_output_transfer(self, outputs):
        flag = False
        outputsafter = [o for o in outputs if self.is_asset_transfer(o['txid'], o['cid'])]
        # print("len(outputs)-->",len(outputs))
        if len(outputsafter) != 0:
            flag = True
        return flag

    def get_outputs_filtered_include_freeze(self, owner, contract_id, include_spent=True):
        """
        Get a list of output links filtered on some criteria
        """
        outputs = self.get_outputs_include_freeze(owner)
        if not include_spent:
            outputs = self.filter_unspent(outputs)
        return outputs

    def get_outputs_filtered_not_include_freeze(self, owner, include_spent=True):
        """
        Get a list of output links filtered on some criteria
        """
        outputs = self.get_outputs_not_include_freeze(owner)

        if not include_spent:
            outputs = self.filter_unspent(outputs)
        # return [u.to_dict() for u in outputs]
        return outputs

    def get_freeze_outputs_only(self, owner, include_spent=True):
        """
        Get a list of output links filtered on some criteria
        """
        outputs = self.only_get_freeze_outputs(owner)

        if not include_spent:
            outputs = self.filter_unspent(outputs)
        # return [u.to_dict() for u in outputs]
        return outputs

    def get_freeze_output(self, owner, contract_id, task_id, task_num, include_spent=True):
        """
        :param owner:
        :param contract_id:
        :param task_id:
        :param task_num:
        :param include_spent:
        :return: outputs,
                flag(
                    0:no asset was frozen;
                    1:the asset was frozen;
                    2:the frozen asset had unfreeze
                    3:the frozen asset had transfer
                    4:has muti-frozen asset
                    )
        """
        outputs = self.get_outputs_freeze(owner, contract_id, task_id, task_num)
        if len(outputs) == 0:
            # print("0---")
            return 0, outputs

        if not include_spent:
            outputs_after = self.filter_unspent(outputs)

        if len(outputs_after) == 1:
            return 1, outputs_after

        if len(outputs_after) == 0:
            flag = self.check_output_transfer(outputs)
            # print("flag-->",flag)
            if flag:
                # TODO return the outputs_after or outputs?
                return 3, outputs_after
            return 2, outputs_after
        return 4, outputs_after

    def get_freeze_output_by_id(self, transaction_id, include_spent=True):
        """
        :param owner:
        :param transaction_id:
        :param include_spent:
        :return: outputs,
                flag(
                    0:no asset was frozen;
                    1:the asset was frozen;
                    2:the frozen asset had unfreeze
                    3:the frozen asset had transfer
                    4:has muti-frozen asset
                    )
        """
        outputs = self.get_outputs_freeze_by_id(transaction_id)
        if len(outputs) == 0:
            # print("0---")
            return 0, outputs

        if not include_spent:
            outputs_after = self.filter_unspent(outputs)

        if len(outputs_after) == 1:
            return 1, outputs_after

        if len(outputs_after) == 0:
            flag = self.check_output_transfer(outputs)
            # print("flag-->",flag)
            if flag:
                # TODO return the outputs_after or outputs?
                return 3, outputs_after
            return 2, outputs_after
        return 4, outputs_after

    def gettxRecordByPubkey(self, pubkey, pageSize, pageNum, start, end):
        startIndex = pageSize * (pageNum - 1)
        endIndex = pageSize * pageNum

        startTime = '1262275200000'  # 2010-01-01 00:00:00
        endTime = gen_timestamp()

        if start is None or end is None:
            res = self.backend.get_tx_record_by_pubkey(pubkey, startIndex, endIndex, startTime, endTime)
        else:
            res = self.backend.get_tx_record_by_pubkey(pubkey, startIndex, endIndex, start, end)
        # res[0],res[1]
        for i, u in enumerate(res[1]):
            if res[1][i]["product_id"]:
                res[1][i]["product_id"] = res[1][i]["product_id"]["ContractBody"]["ContractProductId"]
                res[1][i]["contract_id"] = res[1][i]["contract_id"]["ContractBody"]["ContractId"]
        # block election
        valid_record = []
        for tx in res[1]:
            # disregard transactions from invalid/undecided blocks
            validity = self.get_blocks_status_containing_tx(tx['id'])
            if Bigchain.BLOCK_VALID not in validity.values():
                continue
            valid_record.append(tx)
        return [res[0], valid_record]

    def get_tx_from_backlog(self):
        return self.backend.get_tx_from_backlog(self.me)

    def update_assign_is_deal(self, tx_id):
        return self.backend.update_assign_is_deal(tx_id)

    def update_assign_flag_limit(self, start=0, end=1000):
        if self.split_backlog:
            node_name = self.me[0:5]
        else:
            node_name = ''
        return self.backend.update_assign_flag_limit(self.me, start=start, end=end, node_name=node_name)

    def get_exist_txs(self, tx_ids):
        tx_ids_all = self.backend.is_exist_txs(tx_ids)
        return list(set(tx_ids_all).intersection(set(tx_ids)))

    def get_contract_by_id(self, contract_id):
        return self.backend.get_contract_by_id(contract_id)

    def get_contract_txs_by_tx_id(self, tx_id):
        return self.backend.get_contract_txs_by_id(tx_id)

    def get_tx_by_contract_hash_id(self, contract_hash_id):
        # need to check the tx is validate or not
        return self.backend.get_tx_by_contract_hash_id(contract_hash_id)

    def get_contract_record_by_contract_id(self):

        pass

    # for border trade start
    def getCustomsList(self, param):
        fuserName = param['fuserName']
        tuserName = param['tuserName']
        itemTitle = param['itemTitle']
        orderCode = param['orderCode']
        start = param['startTime']
        end = param['endTime']
        pageSize = param['pageSize']
        pageNum = param['pageNum']

        startTime = '1262275200000'  # 2010-01-01 00:00:00
        endTime = gen_timestamp()
        if start != '':
            startTime = str(round(mktime(strptime(start, '%Y-%m-%d')) * 1000))
        if end != '':
            endTime = str(round(mktime(strptime(end, '%Y-%m-%d')) * 1000))

        startIndex = pageSize * (pageNum - 1)
        endIndex = pageSize * pageNum

        if fuserName != '':
            customList = self.backend.getCustomsListOfFuser(fuserName, startTime, endTime, startIndex, endIndex)
        elif tuserName != '':
            customList = self.backend.getCustomsListOfTuser(tuserName, startTime, endTime, startIndex, endIndex)
        elif itemTitle != '':
            customList = self.backend.getCustomsListOfTitle(itemTitle, startTime, endTime, startIndex, endIndex)
        elif orderCode != '':
            customList = self.backend.getCustomsListOfCode(orderCode, startTime, endTime, startIndex, endIndex)
        else:
            customList = self.backend.getCustomsList(startTime, endTime, startIndex, endIndex)
        customList.append(pageNum)
        return customList

    def getCustomsDeatil(self, param):
        orderCode = param['orderCode']
        return self.backend.getCustomsDetailOfCode(orderCode)

    def getTaxList(self, param):
        fuserName = param['fuserName']
        tuserName = param['tuserName']
        itemTitle = param['itemTitle']
        orderCode = param['orderCode']
        start = param['startTime']
        end = param['endTime']
        pageSize = param['pageSize']
        pageNum = param['pageNum']

        startTime = '1262275200000'  # 2010-01-01 00:00:00
        endTime = gen_timestamp()
        if start != '':
            startTime = str(round(mktime(strptime(start, '%Y-%m-%d')) * 1000))
        if end != '':
            endTime = str(round(mktime(strptime(end, '%Y-%m-%d')) * 1000))

        startIndex = pageSize * (pageNum - 1)
        endIndex = pageSize * pageNum
        if fuserName != '':
            taxlist = self.backend.getTaxListOfFuser(fuserName, startTime, endTime, startIndex, endIndex)
            for tax in taxlist[1]:
                print(tax)
                url = self.order_api + '/uniledger/v1/bordertrade/apiGetGoosTitle'
                headers = {'content-type': 'application/json'}
                print(tax['orderCode'])
                payload = {
                    "orderCode": tax['orderCode']
                }
                data = json.dumps(payload)
                res = requests.post(url, data=data, headers=headers)
                print(res)
                tax["goodsTitle"] = res.json()

        elif tuserName != '':
            taxlist = self.backend.getTaxListOfTuser(tuserName, startTime, endTime, startIndex, endIndex)
            for tax in taxlist[1]:
                print(tax)
                url = self.order_api + '/uniledger/v1/bordertrade/apiGetGoosTitle'
                headers = {'content-type': 'application/json'}
                print(tax['orderCode'])
                payload = {
                    "orderCode": tax['orderCode']
                }
                data = json.dumps(payload)
                res = requests.post(url, data=data, headers=headers)
                print(res)
                tax["goodsTitle"] = res.json()
        elif orderCode != '':
            taxlist = self.backend.getTaxListOfCode(orderCode, startTime, endTime, startIndex, endIndex)
            for tax in taxlist[1]:
                print(tax)
                url = self.order_api + '/uniledger/v1/bordertrade/apiGetGoosTitle'
                headers = {'content-type': 'application/json'}
                print(tax['orderCode'])
                payload = {
                    "orderCode": tax['orderCode']
                }
                data = json.dumps(payload)
                res = requests.post(url, data=data, headers=headers)
                print(res)
                tax["goodsTitle"] = res.json()
        elif itemTitle != '':
            url = self.order_api + '/uniledger/v1/bordertrade/apiGetOrderCodeByTitle'
            headers = {'content-type': 'application/json'}
            payload = {
                "itemTitle": itemTitle
            }
            data = json.dumps(payload)
            res = requests.post(url, data=data, headers=headers)
            orderCodeList = res.json()
            print(orderCodeList)
            taxlist = self.backend.getTaxListOfTitle(orderCodeList, startTime, endTime, startIndex, endIndex)
            for tax in taxlist[1]:
                tax["goodsTitle"] = itemTitle
            print(taxlist)
        else:
            taxlist = self.backend.getTaxList(startTime, endTime, startIndex, endIndex)
            print("1--", taxlist)
            for tax in taxlist[1]:
                print("2--", tax)
                url = self.order_api + '/uniledger/v1/bordertrade/apiGetGoosTitle'
                headers = {'content-type': 'application/json'}
                print("3--", tax['orderCode'])
                payload = {
                    "orderCode": tax['orderCode']
                }
                data = json.dumps(payload)
                # session = requests.Session()
                # session.trust_env = False
                res = requests.post(url, data=data, headers=headers)
                print("4--", res)
                tax["goodsTitle"] = res.json()
        taxlist.append(pageNum)
        return taxlist

    def getTaxDeatil(self, param):
        orderCode = param['orderCode']

        resTax = self.backend.getTaxDetailOfCode(orderCode)

        url = self.order_api + '/uniledger/v1/bordertrade/apiGetGoosTitle'
        headers = {'content-type': 'application/json'}
        payload = {
            "orderCode": orderCode
        }
        data = json.dumps(payload)
        res = requests.post(url, data=data, headers=headers)
        goodsTitle = res.json()
        return resTax, goodsTitle

    def getOrderCodeByTitle(self, param):
        itemTitle = param['itemTitle']
        orderList = self.backend.getOrderCodeByTitle(itemTitle)
        # print(orderList)
        return list(orderList)

    def getGoosTitleByCode(self, param):
        orderCode = param['orderCode']
        title = self.backend.getGoosTitleByCode(orderCode)
        # print(orderList)
        return ','.join(list(title))
        # for border trade end

    def recharge(self, target, amount, msg):
        # print(verifying_key,signing_key,amount)
        # Digital Asset Definition (e.g. RMB)
        asset = Asset(data={'money': 'RMB'}, data_id='20170628150000', divisible=True)
        # Metadata Definition
        metadata = {'raw': msg}
        # create transaction
        tx = Transaction.create([self.me], [([target], amount)], metadata=metadata, asset=asset)
        # sign with private key
        tx = tx.sign([self.me_private])
        # tx_id = tx.to_dict()['id']
        return tx

    # start user account
    def getAccountInfo(self, param):
        try:
            username = param['username']
        except KeyError:
            username = None
        try:
            role = param['role']
        except KeyError:
            role = None
        try:
            status = param['status']
        except KeyError:
            status = None
        try:
            validFlag = param['validFlag']
        except KeyError:
            validFlag = None

        account_info = self.backend.getAccountInfo(username, role, status, validFlag)

        return account_info

    def getAccountRecord(self, param):
        username = param['username']
        account_record = self.backend.getAccountRecord(username)
        return account_record

        # end user account
