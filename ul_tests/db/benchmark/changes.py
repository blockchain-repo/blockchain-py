import time

import rethinkdb as r

from bigchaindb import Bigchain
from bigchaindb.db.utils import Connection


def update_flag_limit(limit=1000):
    import random
    return connection.run(
        r.table('backlog').limit(limit).update({'assignee_isdeal': random.random()}, return_changes=True))


times = 2000
b = Bigchain()
start = time.time()
connection = Connection()
result = update_flag_limit(times)
end = time.time()
print("end", end)
print("takes", end - start, "seconds")
print("update tx", times / (end - start), "times/s")
print("len of changes", len(result['changes']))
