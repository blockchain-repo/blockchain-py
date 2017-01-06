#!/bin/bash

set -e

#check rethinkdb
echo -e "[INFO]==========check rethinkdb=========="
fab check_rethinkdb

#check localdb
echo -e "[INFO]==========check localdb=========="
fab check_localdb

#check unichain-pro
echo -e "[INFO]==========check unichain_cash pro=========="
fab check_unichain

exit 0
