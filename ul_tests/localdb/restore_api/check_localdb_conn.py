
from extend.localdb.restore.utils.leveldb_utils import LocaldbUtils

ldb = LocaldbUtils()

free_conn = ldb.check_conn_free()

print("localdb is free ? {}".format(free_conn))