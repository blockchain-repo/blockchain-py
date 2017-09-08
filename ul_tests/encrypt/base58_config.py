import base58
import bigchaindb
from bigchaindb.common.util import serialize


config = serialize(bigchaindb.config).encode()
a = base58.b58encode(config)
print(a)
b = base58.b58decode(a)
print(b.decode())
