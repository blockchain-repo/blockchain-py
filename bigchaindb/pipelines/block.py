"""This module takes care of all the logic related to block creation.

The logic is encapsulated in the ``BlockPipeline`` class, while the sequence
of actions to do on transactions is specified in the ``create_pipeline``
function.
"""

import logging
import time
import rethinkdb as r
from multipipes import Pipeline, Node, Pipe

from bigchaindb.monitor import Monitor
from bigchaindb.models import Transaction
from bigchaindb.pipelines.utils import ChangeFeed
from bigchaindb.pipelines.utils_for_backlog import BacklogTxToQueue
from bigchaindb import Bigchain, config

logger = logging.getLogger(__name__)
monitor = Monitor()


class BlockPipeline:
    """This class encapsulates the logic to create blocks.

    Note:
        Methods of this class will be executed in different processes.
    """

    def __init__(self):
        """Initialize the BlockPipeline creator"""
        self.bigchain = Bigchain()
        self.txs = []
        self.txsId = []
        self.starttime = 0
        self.block_size = config['argument_config']['block_pipeline.block_size']+self.bigchain.nodelist.index(self.bigchain.me)*config['argument_config']['block_pipeline.block_size_detal']
        self.block_timeout = config['argument_config']['block_pipeline.block_timeout']

    def filter_tx(self, tx):
        """Filter a transaction.

        Args:
            tx (dict): the transaction to process.

        Returns:
            dict: The transaction if assigned to the current node,
            ``None`` otherwise.
        """
        if tx['assignee'] == self.bigchain.me:
            tx.pop('assignee')
            tx.pop('assignment_timestamp')
            tx.pop('assignee_isdeal')
            return tx

    def validate_tx(self, tx):
        """Validate a transaction.

        Also checks if the transaction already exists in the blockchain. If it
        does, or it's invalid, it's deleted from the backlog immediately.

        Args:
            tx (dict): the transaction to validate.

        Returns:
            :class:`~bigchaindb.models.Transaction`: The transaction if valid,
            ``None`` otherwise.
        """
        logger.debug("Validating transaction %s", tx['id'])
        # print(tx)
        tx.pop('assignee')
        tx.pop('assignment_timestamp')
        tx.pop('assignee_isdeal')
        tx = Transaction.from_dict(tx)
        # if self.bigchain.transaction_exists(tx.id):
        if False:
            # if the transaction already exists, we must check whether
            # it's in a valid or undecided block
            tx, status = self.bigchain.get_transaction(tx.id,include_status=True)
            if status == self.bigchain.TX_VALID or status == self.bigchain.TX_UNDECIDED:
                # if the tx is already in a valid or undecided block,
                # then it no longer should be in the backlog, or added
                # to a new block. We can delete and drop it.
                self.bigchain.delete_transaction(tx.id)
                return None

        if monitor is not None:
            with monitor.timer('validate_transaction', rate=config['statsd']['rate']):
                tx_validated = self.bigchain.is_valid_transaction(tx)
        else:
            tx_validated = self.bigchain.is_valid_transaction(tx)
        # tx_validated = self.bigchain.is_valid_transaction(tx)
        if tx_validated:
            return tx
        else:
            # if the transaction is not valid, remove it from the
            # backlog
            self.bigchain.delete_transaction(tx.id)
            return None

    def create(self, tx, timeout=False):
        """Create a block.

        This method accumulates transactions to put in a block and outputs
        a block when one of the following conditions is true:
        - the size limit of the block has been reached, or
        - a timeout happened.

        Args:
            tx (:class:`~bigchaindb.models.Transaction`): the transaction
                to validate, might be None if a timeout happens.
            timeout (bool): ``True`` if a timeout happened
                (Default: ``False``).

        Returns:
            :class:`~bigchaindb.models.Block`: The block,
            if a block is ready, or ``None``.
        """
        if tx:
            self.txs.append(tx)
            self.txsId.append(tx.id)
            logger.debug("Validated transaction %s, txs.len = %d", tx.id,len(self.txs))
        else:
            self.bigchain.updateHeartbeat(time.time())

        if len(self.txs) == 1:
            # 心跳机制，写Node，时间戳。
            self.bigchain.updateHeartbeat(time.time())
            self.starttime = time.time()
        if len(self.txs) == self.block_size or (timeout and self.txs) or (((time.time()-self.starttime) > self.block_timeout) and self.txs):
            req_result = self.bigchain.get_exist_txs(self.txsId)
            exist_tx = list(set(req_result).intersection(set(self.txsId)))
            if exist_tx:
                for txid in exist_tx:
                    tx, status = self.bigchain.get_transaction(txid, include_status=True)
                    if status == self.bigchain.TX_VALID or status == self.bigchain.TX_UNDECIDED:
                        index = self.txsId.index(txid)
                        self.txsId.remove(self.txsId[index])
                        self.txs.remove(self.txs[index])
            block = self.bigchain.create_block(self.txs)
            self.txs = []
            self.txsId = []
            return block

    def write(self, block):
        """Write the block to the Database.

        Args:
            block (:class:`~bigchaindb.models.Block`): the block of
                transactions to write to the database.

        Returns:
            :class:`~bigchaindb.models.Block`: The Block.
        """
        logger.info('Writing new block %s with %s transactions', block.id, len(block.transactions))
        # logger.info('Write new block %s with %s transactions', block.id, block.transactions)
        # zy@secn
        if monitor is not None:
            # with monitor.timer('write_block', rate=config['statsd']['rate']):
            with monitor.timer('write_block'):
                self.bigchain.write_block(block)
        else:
            self.bigchain.write_block(block)
        # self.bigchain.write_block(block)
        return block

    def delete_tx(self, block):
        """Delete transactions.

        Args:
            block (:class:`~bigchaindb.models.Block`): the block
                containg the transactions to delete.

        Returns:
            :class:`~bigchaindb.models.Block`: The block.
        """
        self.bigchain.delete_transaction(*[tx.id for tx in block.transactions])

        return block


def initial():
    """Return old transactions from the backlog."""

    bigchain = Bigchain()

    return bigchain.connection.run(
        r.table('backlog')
            .between([bigchain.me, r.minval],
                     [bigchain.me, r.maxval],
                     index='assignee__transaction_timestamp')
            .order_by(index=r.asc('assignee__transaction_timestamp')))


# def get_changefeed():
#     """Create and return the changefeed for the backlog."""
#
#     return ChangeFeed('backlog', ChangeFeed.INSERT | ChangeFeed.UPDATE,
#                       prefeed=initial())

def get_tx_in_backlog():
    return BacklogTxToQueue(prefeed=initial())

def create_pipeline():
    """Create and return the pipeline of operations to be distributed
    on different processes."""

    block_pipeline = BlockPipeline()

    pipeline = Pipeline([
        Pipe(maxsize = config['argument_config']['block_pipeline.pipe_maxsize']),
        # Node(block_pipeline.filter_tx),
        Node(block_pipeline.validate_tx, fraction_of_cores=config['argument_config']['block_pipeline.fraction_of_cores']),
        Node(block_pipeline.create, timeout=config['argument_config']['block_pipeline.timeout']),
        Node(block_pipeline.write),
        Node(block_pipeline.delete_tx),
    ])

    return pipeline


def start():
    """Create, start, and return the block pipeline."""
    pipeline = create_pipeline()
    pipeline.setup(indata=get_tx_in_backlog())
    pipeline.start()
    return pipeline
