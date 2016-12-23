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
fab start_docker_bdb

#unichain init&shards&replicas
echo -e "[INFO]=========init unichain========="
#fab init_unichain
echo -e "[INFO]==========set shards unichain=========="
#fab set_shards:${CLUSTER_BIGCHAIN_COUNT}
echo -e "[INFO]==========set replicas unichain=========="
REPLICAS_NUM=`get_replicas_num ${CLUSTER_BICHAIN_COUNT}`
#fab set_replicas:${REPLICAS_NUM}


exit 0
