#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

source ./blockchain_nodes_conf_util.sh
source ./common_lib.sh

CLUSTER_BIGCHAIN_COUNT=`get_cluster_nodes_num`
[ $CLUSTER_BIGCHAIN_COUNT -eq 0 ] && {
    echo -e "[ERROR] blockchain_nodes num is 0"
    exit 1
}


INSTALL_FLAG=false
LOAD_FLAG=false

while getopts "il" arg
do
    case $arg in
        i)
            INSTALL_FLAG=true
        ;;
        l)
            LOAD_FLAG=true
        ;;
        *)
            echo "Usage: run_docker [-i] [-l]"
            echo "-i: install docker & docker compose; -l: load new docker image"
            exit 1
        ;;
    esac
done
echo "1"
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

#bak old conf
echo -e "[INFO]==========bak old conf=========="
./bak_conf.sh "old"

# init unichain directory and configuration file
echo -e "[INFO]========init unichain conf========"
./configure_unichain_for_docker.sh ${CLUSTER_BIGCHAIN_COUNT}
echo -e "[INFO]========down unichain conf========"

# init rethinkdb directory and configuration file
echo -e "[INFO]==========init rethinkdb=========="
./configure_rethinkdb_for_docker.sh
echo -e "[INFO]==========down rethinkdb=========="

# send collectd configuration file
echo -e "[INFO]==========init collected=========="
./configure_collectd_for_docker.sh
echo -e "[INFO]==========down collected=========="


#bak current conf
echo -e "[INFO]==========bak new conf=========="
./bak_conf.sh "new"
