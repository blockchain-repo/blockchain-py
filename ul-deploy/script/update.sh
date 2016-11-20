#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

function printErr()
    {
        echo "usage: ./update.sh <number_of_files>"
        echo "No argument $1 supplied"
    }

if [ -z "$1" ]; then
    printErr "<number_of_files>"
    exit 1
fi

# reconfigure collectd & rethinkdb & unichain
./clustercontrol.sh stop

./configure_collectd.sh
./configure_rethinkdb.sh

#./install_unichain_from_git_archive.sh
./install_unichain_from_local_archive.sh

./configure_unichain.sh $1
#Todo 增加节点的话 需要特别处理？？？？
#fab set_shards:$1

./clustercontrol.sh start

