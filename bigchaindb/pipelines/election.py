"""This module takes care of all the logic related to block status.

Specifically, what happens when a block becomes invalid.  The logic is
encapsulated in the ``Election`` class, while the sequence of actions
is specified in ``create_pipeline``.
"""
import logging

import rethinkdb as r
from multipipes import Pipeline, Node

from bigchaindb.pipelines.utils import ChangeFeed
from bigchaindb.models import Block
from bigchaindb import Bigchain
from time import sleep,time


logger = logging.getLogger(__name__)


class Election:
    """Election class."""

    def __init__(self):
        self.bigchain = Bigchain()
        self.count = 0
        print(self.bigchain.nodelist)

    def check_for_quorum(self, next_vote):
        """
        Checks if block has enough invalid votes to make a decision

        Args:
            next_vote: The next vote.

        """
        next_block = self.bigchain.connection.run(
                r.table('bigchain')
                .get(next_vote['vote']['voting_for_block']))

        block_status = self.bigchain.block_election_status(next_block['id'],
                                                           next_block['block']['voters'])
        if(self.count==0):
            block_status = self.bigchain.BLOCK_INVALID
            self.count+=1
        if block_status == self.bigchain.BLOCK_INVALID:

            return Block.from_dict(next_block)

    def requeue_transactions(self, invalid_block):
        """
        Liquidates transactions from invalid blocks so they can be processed again
        """

        print(self.bigchain.me +"---" + invalid_block.node_pubkey)
        if self.bigchain.me == invalid_block.node_pubkey:
            logger.info('Rewriting %s transactions from invalid block %s',
                        len(invalid_block.transactions),
                        invalid_block.id)
            data = {'id':invalid_block.id,'node_publickey': invalid_block.node_pubkey}
            self.bigchain.insertRewrite(data)
            for tx in invalid_block.transactions:
                self.bigchain.write_transaction(tx)
            return
        # 不是当前节点建的块才返回，进入下一个node
        return invalid_block

    def check_local_mem(self,invalid_block):
        print("check_local_mem")
        sleep(2)
        isHandled = self.bigchain.selectFromWrite(invalid_block.id)
        if not isHandled:
            print("is not handle")
            nodeIndex = self.bigchain.nodelist.index(invalid_block.node_pubkey)
            myIndex = self.bigchain.nodelist.index(self.bigchain.me)
            # 计算到什么时间才需要当前node处理
            if nodeIndex > myIndex:
                endtime = time() + (nodeIndex - myIndex) * 10 # 每个节点需要10s钟处理时间，
            else:
                endtime = time() + (len(self.bigchain.nodelist) - nodeIndex + myIndex) * 10
            # 在到截止时间的过程中，不断的去查询这个block是否已经处理了。
            while(endtime >time()):
                print(".."+ str(endtime) +"--"+time())
                sleep(2)
                isHandled = self.bigchain.selectFromWrite(invalid_block.id)
                if isHandled:
                    return
            # 当while执行完的时候，说明前边的节点没有处理，该当前节点处理了。
            logger.info(' Rewriting %s transactions from invalid block %s --check_local_mem',
                        len(invalid_block.transactions),
                        invalid_block.id)
            for tx in invalid_block.transactions:
                self.bigchain.write_transaction(tx)
            return invalid_block
        return

def get_changefeed():
    return ChangeFeed(table='votes', operation=ChangeFeed.INSERT)


def create_pipeline():
    election = Election()

    election_pipeline = Pipeline([
        Node(election.check_for_quorum),
        Node(election.requeue_transactions),
        Node(election.check_local_mem)
    ])

    return election_pipeline


def start():
    pipeline = create_pipeline()
    pipeline.setup(indata=get_changefeed())
    pipeline.start()
    return pipeline
