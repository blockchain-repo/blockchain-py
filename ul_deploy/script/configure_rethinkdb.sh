#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

# (Re)create the RethinkDB configuration file conf/rethinkdb.conf
echo -e "[INFO]==========init rethinkdb conf=========="
python3 create_rethinkdb_conf.py

# Rollout storage backend (RethinkDB) and start it
echo -e "[INFO]=========configure rethinkdb========="
fab configure_rethinkdb

exit 0
