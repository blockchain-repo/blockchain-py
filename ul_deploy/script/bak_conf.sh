#!/bin/bash


if [ $# -lt 1 ];then
    echo -e "[ERROR] bak_conf.sh need 1 param(old|new)!!!"
    exit 1
elif [ $1 != "new" -a $1 != "old" ];then
    echo -e "[ERROR] bak_conf.sh need 1 param(old|new),input is $1!!!"
    exit 1
fi

source ./common_lib.sh


case $1 in
    "old")
        date_str=`date +"%Y%m%d%H%M%S"`
        init_bak_old_dir ${date_str}
        bak_old_base_path=${BAK_BASE_PATH}/${date_str}/conf
        cp -rf ../conf/blockchain_nodes ${bak_old_base_path}/cluster/ 2>/dev/null
        fab bak_rethinkdb_conf:"${bak_old_base_path}"
        fab bak_collected_conf:"${bak_old_base_path}" 
        fab bak_unichain_conf:"${bak_old_base_path}" 
    ;;
    "new")
        init_bak_current_dir
        bak_new_base_path=${BAK_BASE_PATH}/now/conf
        cp -rf ../conf/blockchain_nodes ${bak_new_base_path}/cluster/ 2>/dev/null
        fab bak_rethinkdb_conf:"${bak_new_base_path}"
        fab bak_collected_conf:"${bak_new_base_path}" 
        fab bak_unichain_conf:"${bak_new_base_path}" 
    ;;
esac 

exit 0
