#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

function printErr()
{
    echo "usage: ./update.sh <number_of_files>"
    echo "No argument $1 supplied"
}

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
     echo -e "[INFO]=========begin update=========="
else
    echo -e "[ERROR]input invalid or cluster nodes info invalid"
    echo -e "[ERROR]=========update aborted==========="
    exit 1
fi

CLUSTER_BIGCHAIN_COUNT=`get_cluster_nodes_num`
[ $CLUSTER_BIGCHAIN_COUNT -eq 0 ] && {
    echo -e "[ERROR] blockchain_nodes num is 0"
    exit 1
}

#clusternodes stop
echo -e "[INFO]==========stop clusternodes=========="
./clustercontrol.sh stop

#collectd&rethinkdb&unichain reconfigure
echo -e "[INFO]==========configure collectd=========="
./configure_collectd.sh
echo -e "[INFO]==========configure rethinkdb=========="
./configure_rethinkdb.sh
echo -e "[INFO]==========reinstall chain=========="
./install_unichain_from_local_archive.sh
echo -e "[INFO]==========configure unchain=========="
./configure_unichain.sh ${CLUSTER_BIGCHAIN_COUNT}


#Todo 增加节点的话 需要特别处理？？？？
#fab set_shards:$1

#clusternodes start
echo -e "[INFO]==========start clusternodes=========="
./clustercontrol.sh start

exit 0
