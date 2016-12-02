#!/bin/bash

CUR_PATH=$(cd "$(dirname "$0")"; pwd)
CLUSTER_CHAINNODES_CONF=${CUR_PATH}/../conf/blockchain_nodes

source ./common_lib.sh

#check conf/blockchain_nodes format
function check_cluster_nodes_conf
{
    [ ! -s $CLUSTER_CHAINNODES_CONF ] && {
        echo "[ERROR] blockchain_nodes conf not exist!"
        return 1
    }
    local str_content=`cat $CLUSTER_CHAINNODES_CONF|grep -vE "^#|^$"`
    [ -z "$str_content" ] && {
        echo "[ERROR] blockchain_nodes conf is null!"
        return 1
    }
    #check format
    local format="[a-zA-Z0-9_\-]+@[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+[ ]+[^ ]+"
    local cl_num=`cat $CLUSTER_CHAINNODES_CONF|grep -vE "^#|^$"|grep -vE "$format"|wc -l`
    [ $cl_num -gt 0 ] && {
        echo -e "[ERROR] blockchain_nodes contents format error!"
        echo -e "\tFORMAT:username@host:port password"
        return 1
    }
    #check ip duplication
    local duplicat_host=`cat $CLUSTER_CHAINNODES_CONF|grep -vE "^#|^$"|grep -o "@.*:"|sed "s/@\|://g"|sort|uniq -c|sed "s/^[ ]*//g"|grep -v "^1 "|awk '{print $2}'`
    [ ! -z $duplicat_host  ] && {
        echo -e "[ERROR] blockchain_nodes continues multi same host[$duplicat_host]!!!"
        return 1
    }
    return 0
}

#get nodes num from conf/blockchain_nodes
function get_cluster_nodes_num
{
    local format="[a-zA-Z0-9_\-]+@[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+[ ]+[^ ]+"
    local nodes_num=`cat $CLUSTER_CHAINNODES_CONF|grep -vE "^#|^$"|grep -E "$format"|wc -l`
    echo $nodes_num
    return 0
}

#check blockchain_nodes cluster diff
function check_blocknodes_diff()
{
    local last_conf=${BAK_BASE_PATH}/now/conf/cluster/blockchain_nodes
    local now_conf=${CUR_PATH}/../conf/blockchain_nodes
    if [ ! -f $now_conf ];then
        echo -e "[ERROR]conf/blockchain_nodes not exist!!!"
        exit 1
    fi
    if [ ! -f $last_conf ];then
        echo -e "[ERROR]bak of first_setup blockchain_nodes is not exist!!!continue will accur an unknown error!!! "
        exit 1
    fi
    local diff_num=`cat $last_conf $now_conf 2>/dev/null|grep -vE "^#|^$"|sort|uniq -c|sed "s/^[ ]*//g"|grep  "^1 "|wc -l`
    if [ $diff_num -gt 0 ];then
        echo -e "[ERROR] blockchain_nodes has diff,cluster nodes are not same as first_setup"
        return 1
    fi
    return 0
}
