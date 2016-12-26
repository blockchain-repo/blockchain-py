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
        ?)
            echo "Usage: run_docker [-i] [-l]"
            echo "-i: install docker & docker compose; -l: load new docker image"
            exit 1
        ;;
    esac
done

#install docker and docker-compose: necessary for the first install
if [ $INSTALL_FLAG != false ];then
    echo -e "[INFO]==========install docker========="
    fab install_docker
fi

#load docker image
if [ $LOAD_FLAG != false ];then
    echo -e "[INFO]==========load docker image========="
    fab load_image
fi


#rethinkdb & unichain configure
echo -e "[INFO]==========configure rethinkdb=========="
#./configure_rethinkdb.sh
python3 create_rethinkdb_conf.py
fab configure_rethinkdb_for_docker
echo -e "[INFO]=========configure unichain========="
./configure_unichain_for_docker.sh ${CLUSTER_BIGCHAIN_COUNT}

#
echo -e "[INFO]==========start service=========="
fab start_docker_rdb
#unichain init&shards&replicas
echo -e "[INFO]=========init unichain========="
REPLICAS_NUM=`gen_replicas_num ${CLUSTER_BIGCHAIN_COUNT}`
fab start_docker_bdb_init:num_shards=${CLUSTER_BIGCHAIN_COUNT},num_replicas=${REPLICAS_NUM}
#
fab start_docker_bdb


exit 0
