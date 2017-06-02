"""This module monitors for stale transactions.

It reassigns transactions which have been assigned a node but
remain in the backlog past a certain amount of time.
"""

import logging
from bigchaindb.monitor import Monitor
from multipipes import Pipeline, Node
from bigchaindb import Bigchain,config
from time import sleep,time


logger = logging.getLogger(__name__)
monitor = Monitor()


class StaleTransactionMonitor:
    """This class encapsulates the logic for re-assigning stale transactions.

    Note:
        Methods of this class will be executed in different processes.
    """

    def __init__(self, timeout=10, backlog_reassign_delay=None):
        """Initialize StaleTransaction monitor

        Args:
            timeout: how often to check for stale tx (in sec)
            backlog_reassign_delay: How stale a transaction should
                be before reassignment (in sec). If supplied, overrides
                the Bigchain default value.
        """
        self.bigchain = Bigchain(backlog_reassign_delay=backlog_reassign_delay)
        self.timeout = config['argument_config']['stale_pipeline.timeout']

    def check_transactions(self):
        """Poll backlog for stale transactions

        Returns:
            txs (list): txs to be re assigned
        """
        sleep(self.timeout)
        # 当前节点
        mykey = self.bigchain.me

        # 有reassignee权限的node key

        total_transaction_count =self.bigchain.get_txNumber()
        total_block_count = self.bigchain.get_BlockNumber()
        invalid_block_count = self.bigchain.get_allInvalidBlock_number()
        invalid_block_rate = invalid_block_count / total_block_count

        # 交易总数
        monitor.gauge('total_transaction_count', value=total_transaction_count)
        # 区块总数
        monitor.gauge('total_block_count', value=total_block_count)
        # 无效区块数
        monitor.gauge('invalid_block_count', value=invalid_block_count)
        # 无效块占比
        monitor.gauge('invalid_block_rate', value=invalid_block_rate)

        nodeid, assigneekey = self.bigchain.getAssigneekey()
        # TODO update ,1st check nodes 2st check txs
        if mykey == assigneekey:
            # print("i am the reassignee node. select need reassign tx")
            # 记录assignee心跳，并取出要处理的tx
            self.bigchain.updateAssigneebeat(assigneekey,time())
            # zy@secn
            monitor.gauge('tx_queue_gauge', value=self.bigchain.get_backlog_tx_number())
            for tx in self.bigchain.get_stale_transactions():
                yield tx
        else:
            monitor.gauge('tx_queue_gauge', value=0)
            # 如果当前节点没有reassignee权限，则需要判断有reassignee权限的节点是否down掉
            isalive = self.bigchain.is_assignee_alive(assigneekey, config['argument_config']['stale_pipeline.assignee_timeout'])
            if not isalive:
                # print("i am not the reassignee node. the assign node is dead! %d" % (time()))
                # 更新reassign的节点。
                updateid = int((nodeid + 1) % (len(self.bigchain.nodelist)))
                next_assign_node = self.bigchain.nodelist[updateid]
                self.bigchain.update_assign_node(updateid, next_assign_node)
                return
            # 如果alive，不操作，等待reassignee node去处理
            # print("i am not the reassignee node. the assign node is alive!")
            return



    def reassign_transactions(self, tx):
        """Put tx back in backlog with new assignee

        Returns:
            transaction
        """
        # tx被指派的节点
        txpublickey = tx["assignee"]
        isalive = self.bigchain.is_node_alive(txpublickey,config['argument_config']['stale_pipeline.heartbeat_timeout'])
        if not isalive:
            # print("i am the reassignee node. the tx node is dead. need to be reassignee!")
            # node down ，需要reassign tx
            logger.info('Reassigning transaction id %s', tx['id'])
            self.bigchain.reassign_transaction(tx)
            return tx
        # 如果alive，就是阻塞，不需要reassignee
        # print("i am the reassignee node. the tx node is alive. just wait!")
        return


def create_pipeline(timeout=10, backlog_reassign_delay=30):
    """Create and return the pipeline of operations to be distributed
    on different processes."""

    stm = StaleTransactionMonitor(timeout=timeout,
                                  backlog_reassign_delay=backlog_reassign_delay)

    monitor_pipeline = Pipeline([
        Node(stm.check_transactions),
        Node(stm.reassign_transactions)
    ])

    return monitor_pipeline


def start(timeout=10, backlog_reassign_delay=20):
    """Create, start, and return the block pipeline."""
    pipeline = create_pipeline(timeout=timeout,
                               backlog_reassign_delay=backlog_reassign_delay)
    pipeline.start()
    return pipeline
