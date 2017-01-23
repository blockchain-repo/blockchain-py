#!/bin/bash

##############################################
###  check for other except set_up        ####
##############################################

#Args: $1 => shards_num(cluster nodes num)
function gen_replicas_num()
{
    local nodes_num=$1
    local replicas_num=1
    if [ $nodes_num -le 0 ];then
        replicas_num=1
    elif [[ $nodes_num -ge 1 && $nodes_num -le 3 ]];then
        replicas_num=$nodes_num
    else
        replicas_num=$(($nodes_num/2+1))
    fi
    echo $replicas_num
    return 0    
}


BAK_BASE_PATH=~/`pwd|awk -F"/" '{print $4}'`"_BAKUP"
#bak deployed conf
#Args: $1 => date_str
function init_bak_old_dir()
{
    local date_str=$1
    mkdir -p ${BAK_BASE_PATH}/${date_str}/conf/{cluster,unichain,rethinkdb,leveldb,collected}
    return 0
}

function init_bak_current_dir()
{
    mkdir -p ${BAK_BASE_PATH}/now/conf/{cluster,unichain,rethinkdb,leveldb,collected}
    return 0
}
