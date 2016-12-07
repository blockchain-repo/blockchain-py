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
if [[ $# -eq 1 && $1 == "nostart" ]];then
    AUTO_START_FLAG=0
else
    AUTO_START_FLAG=1
fi
source ./blockchain_nodes_conf_util.sh
source ./common_lib.sh

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

#check if cluster conf diff
echo -e "[INFO]==========check cluster conf diff=========="
check_blocknodes_diff

#bak old conf
echo -e "[INFO]==========bak old conf=========="
./bak_conf.sh "old"

#clusternodes stop
echo -e "[INFO]==========stop clusternodes=========="
./clustercontrol.sh stop

#collectd&rethinkdb&unichain reconfigure
echo -e "[INFO]==========configure collectd=========="
./configure_collectd.sh
echo -e "[INFO]==========configure rethinkdb=========="
./configure_rethinkdb.sh
echo -e "[INFO]==========reinstall chain=========="
./install_unichain_archive.sh "local"
echo -e "[INFO]==========configure unchain=========="
./configure_unichain.sh ${CLUSTER_BIGCHAIN_COUNT}


#Todo 增加节点的话 需要特别处理？？？？
#fab set_shards:$1

#bak current conf
echo -e "[INFO]==========bak new conf=========="
./bak_conf.sh "new"

if [[ -z $AUTO_START_FLAG || $AUTO_START_FLAG -eq 1 ]];then
    #start unichain nodes
    echo -e "[INFO]==========start unichain nodes=========="
    ./clustercontrol.sh start
    ./run_server_check.sh
fi

exit 0
