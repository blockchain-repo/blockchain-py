"""This module takes care of all the logic related to block creation.

The logic is encapsulated in the ``BlockPipeline`` class, while the sequence
of actions to do on transactions is specified in the ``create_pipeline``
function.
"""

import logging
import time
from multipipes import Pipeline, Node, Pipe
from ul_tests.apiForDemoTest.test_util_queue import AddTxToQueue

logger = logging.getLogger(__name__)


class TestPipline:
    def __init__(self):
        self.count = 0
        self.txs = []

    def filter_tx(self, tx):
        self.count = self.count +1
        return tx

    def create(self,tx):
        if tx:
            self.txs.append(tx)
        print(":::",time.time()*1000,":::len txs::",len(self.txs))

def get_tx_in_backlog():
    return AddTxToQueue()

def create_pipeline():
    testPipline =TestPipline()
    pipeline = Pipeline([
        Pipe(maxsize = 5000),
        Node(testPipline.filter_tx,fraction_of_cores=5),
        Node(testPipline.create),
    ])
    return pipeline


def start():
    """Create, start, and return the block pipeline."""
    pipeline = create_pipeline()
    pipeline.setup(indata=get_tx_in_backlog())
    pipeline.start()
    return pipeline


