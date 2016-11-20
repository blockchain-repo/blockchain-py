#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

function printErr()
    {
        echo "usage: ./first_setup.sh <number_of_files>"
        echo "No argument $1 supplied"
    }

if [ -z "$1" ]; then
    printErr "<number_of_files>"
    exit 1
fi

#must remove old
fab uninstall_unichain

# necessary for the first install unichain
fab install_base_software

#collectd
fab install_collectd
#configure collectd
./configure_collectd.sh

fab install_rethinkdb
./configure_rethinkdb.sh

#install localdb
#fab install localdb

./install_unichain_from_git_archive.sh
./configure_unichain.sh $1
fab init_unichain

fab set_shards:$1
./clustercontrol.sh start
