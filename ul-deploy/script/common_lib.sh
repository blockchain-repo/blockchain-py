#!/bin/bash

##############################################
###  check for other except set_up        ####
##############################################

function gen_replicas_num()
{
    local nodes_num = $1
    local replicas_num = 1
    if [ $nodes_num -lt 0 ];then
        replicas_num = 1
    elif [ $nodes_num -ge 1 && $nodes_num -le 2 ];then
        replicas_num = $nodes_num
    else
        replicas_num = ($nodes_num / 2) + 1
    fi
    echo $replicas_num
    return 0   
}
