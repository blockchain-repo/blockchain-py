from bigchaindb.common.transaction import Transaction
from bigchaindb.common import crypto

import sha3


tx_body_serialized = "hello unichain 2017"
valid_tx_id1 = Transaction._to_hash(tx_body_serialized)
valid_tx_id2 = crypto.hash_data(tx_body_serialized)
valid_tx_id3 = sha3.sha3_256(tx_body_serialized.encode()).hexdigest()
print(valid_tx_id1)
print(valid_tx_id2)
print(valid_tx_id3)