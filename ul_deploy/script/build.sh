#!/bin/bash
#####################################
##  Install the deployment portal  ##
#####################################

mkdir -p ../log

function echo_green
{
    local content=$@
    echo -e "\033[1;32m${content}\033[0m"
    return 0
}

function usage
{
    echo_green "
Usage:
    $0 [\$1]
Options:
    h|-h|help|-help usage help
    env_check    before setup, check tools already in env
    first_setup  \$1: nostart, if set \$1,it cann't start nodes after setup
                 first setup:
                    sence: first setup use
                    op: a.install base tools|depends libs|rethinkdb|bigchaindb|unichain
                        b.configure rethinkdb|bigchaindb|unichain
                        c.start cluster nodes server
    update       \$1: nostart, if set \$1,it cann't start nodes after update
                 update setup:
                    sence: a. when unichain pro  is updated
                           b. when unichain conf is updated
                           c. when update fail, need rollback
                    op: a.update unichain
                        b.reconfigure rethinkdb|bigchaindb|unichain
                        c.restart cluster nodes server
    server_check after setup, check servers in cluster nodes are running
    start_all    start all cluster nodes
    stop_all     stop  sll cluster nodes
    start_node   start signal cluster node 
    stop_node    stop  signal cluster node
    single_setup reinstall single cluster node
    uninstall    uninstall unichain
    "
    return 0
}

chmod +755 *.sh 2>/dev/null
chmod +755 *.py 2>/dev/null

case $1 in
    h|help|-h|-help)
        usage
    ;;
    env_check)
        ./run_env_check.sh | tee ../log/run_env_check.sh
    ;;
    first_setup)
        str_param=`echo $@|awk '{for(i=2;i<=NF;i++){if(i!=NF)print $i" ";else print $i}}'`
        ./run_first_setup.sh $str_param | tee ../log/run_first_setup.log
    ;;
    update)
        str_param=`echo $@|awk '{for(i=2;i<=NF;i++){if(i!=NF)print $i" ";else print $i}}'`
        ./run_update.sh $str_param | tee ../log/run_update.log
    ;;
    server_check)
        ./run_server_check.sh | tee ../log/run_server_check.log
    ;;
    start_all)
        ./clustercontrol.sh start | tee ../log/clustercontrol_start.log
        ./run_server_check.sh | tee ../log/run_server_check.log 
    ;;
    stop_all)
        ./clustercontrol.sh stop | tee ../log/clustercontrol_stop.log
        ./run_server_check.sh | tee ../log/run_server_check.log
    ;;
    start_node)
        str_param=`echo $@|awk '{for(i=2;i<=NF;i++){if(i!=NF)print $i" ";else print $i}}'`
        ./startnode.sh $str_param | tee ../log/startnode.log
    ;;
    stop_node)
        str_param=`echo $@|awk '{for(i=2;i<=NF;i++){if(i!=NF)print $i" ";else print $i}}'`
        ./stopnode.sh $str_param | tee ../log/stopnode.log
    ;;
    single_setup)
        str_param=`echo $@|awk '{for(i=3;i<=NF;i++){if(i!=NF)print $i" ";else print $i}}'`
        ./single_setup.sh $str_param | tee ../log/single_setup.log
    ;;
    uninstall)
        ./run_uninstall.sh | tee ../log/uninstall.log
    ;;
    *)
        usage
    ;;
esac

exit 0
