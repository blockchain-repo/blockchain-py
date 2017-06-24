"""This module monitors for grafana.

It will send unichain data to influxdb,and display it on grafana.
"""

import logging
from bigchaindb.monitor import Monitor
from multipipes import Pipeline, Node
from bigchaindb import Bigchain,config
from time import sleep,time


logger = logging.getLogger(__name__)
monitor = Monitor()


class UnichainStaticDataMonitor:
    """This class will query unichain static data and send infulxdb
    """

    def __init__(self, timeout=10):
        """Initialize UnichainStaticDataMonitor monitor
        Args:
            timeout: how often to check for stale tx (in sec)
        """
        self.timeout = config['argument_config']['stale_pipeline.timeout']


    def send_static_data(self):
        sleep(self.timeout)
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
        # blocklog 中数据
        monitor.gauge('tx_queue_gauge', value=self.bigchain.get_backlog_tx_number())



def create_pipeline(timeout=10):
    """Create and return the pipeline of operations to be distributed
    on different processes."""

    usdm = UnichainStaticDataMonitor(timeout=timeout)

    monitor_pipeline = Pipeline([
        Node(usdm.send_static_data)
    ])

    return monitor_pipeline


def start(timeout=10):
    """Create, start, and return the block pipeline."""
    pipeline = create_pipeline(timeout=timeout)
    pipeline.start()
    return pipeline
