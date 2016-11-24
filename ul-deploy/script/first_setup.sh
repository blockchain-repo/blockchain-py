#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

function printErr()
{
     echo "usage: ./first_setup.sh <number_of_files>"
     echo "No argument $1 supplied"
}
##get it from ../conf/blockchain_nodes 
#if [ -z "$1" ]; then
#    printErr "<number_of_files>"
#    exit 1
#fi

source ./blockchain_nodes_conf_util.sh

##check blocknodes_conf format
echo -e "[INFO]==========check cluster nodes conf=========="
check_cluster_nodes_conf || {
    echo -e "[ERROR] $FUNCNAME execute fail!"
    exit 1
}

echo -e "[INFO]==========cluster nodes info=========="
cat $CLUSTER_CHAINNODES_CONF|grep -vE "^#|^$"
echo -e ""

echo -e "[WARNING]please confirm cluster nodes info: [y/n]"
read cluster_str
if [ "`echo "$cluster_str"|tr A-Z  a-z`" == "y" -o "`echo "$cluster_str"|tr A-Z  a-z`" == "yes" ];then
	 echo -e "[INFO]=========begin first_setup=========="
else
	echo -e "[ERROR]input invalid or cluster nodes info invalid"
	echo -e "[ERROR]=========first_setup aborted==========="
    exit 1
fi

CLUSTER_BIGCHAIN_COUNT=`get_cluster_nodes_num`
[ $CLUSTER_BIGCHAIN_COUNT -eq 0 ] && {
    echo -e "[ERROR] blockchain_nodes num is 0"
    exit 1
}


#must remove old
echo -e "[INFO]==========uninstall unichain=========="
fab uninstall_unichain

#base sofeware install: necessary for the first install
echo -e "[INFO]==========install base sofeware========="
fab install_base_software

#collectd install&configure
echo -e "[INFO]==========install collectd========="
fab install_collectd
echo -e "[INFO]==========configure collectd========="
./configure_collectd.sh

#rethinkdb install&configure
echo -e "[INFO]==========install  rethinkdb=========="
fab install_rethinkdb
echo -e "[INFO]==========configure  rethinkdb=========="
./configure_rethinkdb.sh

#localdb install
echo -e "[INFO]==========install localdb=========="
#fab install localdb

#unichain install&configure&init&shards
echo -e "[INFO]==========install unichain=========="
./install_unichain_from_git_archive.sh
echo -e "[INFO]=========configure unichain========="
./configure_unichain.sh ${CLUSTER_BIGCHAIN_COUNT}
echo -e "[INFO]=========init unichain========="
fab init_unichain
echo -e "[INFO]==========set shards unichain========="
fab set_shards:${CLUSTER_BIGCHAIN_COUNT}

#start unichain nodes
echo -e "[INFO]==========start unichain nodes========="
./clustercontrol.sh start

exit 0
