"""This module monitors for stale transactions.

It reassigns transactions which have been assigned a node but
remain in the backlog past a certain amount of time.
"""

import logging
from bigchaindb.monitor import Monitor
from multipipes import Pipeline, Node
from bigchaindb import Bigchain
from time import sleep


logger = logging.getLogger(__name__)
monitor = Monitor()


class StaleTransactionMonitor:
    """This class encapsulates the logic for re-assigning stale transactions.

    Note:
        Methods of this class will be executed in different processes.
    """

    def __init__(self, timeout=5, backlog_reassign_delay=None):
        """Initialize StaleTransaction monitor

        Args:
            timeout: how often to check for stale tx (in sec)
            backlog_reassign_delay: How stale a transaction should
                be before reassignment (in sec). If supplied, overrides
                the Bigchain default value.
        """
        self.bigchain = Bigchain(backlog_reassign_delay=backlog_reassign_delay)
        self.timeout = timeout

    def check_transactions(self):
        """Poll backlog for stale transactions

        Returns:
            txs (list): txs to be re assigned
        """
        sleep(self.timeout)
        # zy@secn
        monitor.gauge('tx_queue_gauge', value=self.bigchain.get_backlog_tx_number())
        for tx in self.bigchain.get_stale_transactions():
            yield tx

    def reassign_transactions(self, tx):
        """Put tx back in backlog with new assignee

        Returns:
            transaction
        当且仅当reassignee node是当前节点，且tx被指派的节点down，才会执行reassignee
        """
        # tx被指派的节点
        txpublickey = tx["assignee"]
        # print("txpublickey"+txpublickey)

        # 当前节点
        mykey = self.bigchain.me
        # print("mykey"+mykey)

        # 有reassignee权限的node key
        nodeid,assigneekey = self.bigchain.getAssigneekey()
        print("nodeid.."+str(nodeid)+",assigneekey.."+assigneekey)

        if mykey == assigneekey:
            # 判断tx被指派的node是否alive
            isalive = self.bigchain.is_node_alive(txpublickey,10)
            if not isalive:
                # node down ，需要reassign tx
                self.bigchain.reassign_transaction(tx)
                return tx
            # 如果alive，就是阻塞，不需要reassignee
            return
        else:
            # 如果当前节点没有reassignee权限，则需要判断有reassignee权限的节点是否down掉
            isalive = self.bigchain.is_node_alive(assigneekey, 10) # TODO 根据心跳还是assignee表，单个pipline挂掉？ assingee还需要时间戳吗
            if not isalive:
                # 更新reassign的节点。 TODO 可能会有多个Node同时update？不过没有影响
                # nowid = self.bigchain.get_node_id(assigneekey)
                updateid = (nodeid+1)/(len(self.bigchain.nodes_except_me)+1)
                next_assign_node = self.bigchain.get_node_key(updateid)
                self.bigchain.update_assign_node(updateid,next_assign_node)
                return
            # 如果alive，不操作，等待reassignee node去处理
            return

def create_pipeline(timeout=5, backlog_reassign_delay=5):
    """Create and return the pipeline of operations to be distributed
    on different processes."""

    stm = StaleTransactionMonitor(timeout=timeout,
                                  backlog_reassign_delay=backlog_reassign_delay)

    monitor_pipeline = Pipeline([
        Node(stm.check_transactions),
        Node(stm.reassign_transactions)
    ])

    return monitor_pipeline


def start(timeout=5, backlog_reassign_delay=5):
    """Create, start, and return the block pipeline."""
    pipeline = create_pipeline(timeout=timeout,
                               backlog_reassign_delay=backlog_reassign_delay)
    pipeline.start()
    return pipeline
