#!/bin/bash

CUR_PATH=$(cd "$(dirname "$0")"; pwd)
CLUSTER_CHAINNODES_CONF=${CUR_PATH}/../conf/blockchain_nodes

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
	return 0
}

function get_cluster_nodes_num
{
	local format="[a-zA-Z0-9_\-]+@[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+[ ]+[^ ]+"
    local nodes_num=`cat $CLUSTER_CHAINNODES_CONF|grep -vE "^#|^$"|grep -E "$format"|wc -l`
	echo $nodes_num
	return 0
}
