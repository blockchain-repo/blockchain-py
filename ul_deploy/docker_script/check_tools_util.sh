#!/bin/bash

###########################################
##          check env tools              ##
##  function name: check_tooname_version ##
###########################################

##output: python_bin|python_bin_path
function get_all_python
{
    for p_python in `whereis python|sed "s/$/ /g"|grep -oE "/[a-zA-Z/]+/bin/python[.0-9]+[ ]+"|sort -u`
    do
        bin_python=`echo -e "$p_python"|awk -F"/" '{print $NF}'`
        #v_cmd_python="${bin_python} --version"
        echo -e "$bin_python|$p_python"
    done
    return 0
}

function check_python_3
{
    for t_line in `get_all_python`
    do
        bin_python=`echo $t_line|awk -F"|" '{print $1}'`
        if [ ! -z `echo $bin_python|grep "python3"` ];then
            echo $bin_python
            return 0
        fi
    done
    return 0
}

function get_python_bin_path
{
    local python_bin=$1
    if [ -z $python_bin ];then
        return 0
    fi
    whereis $python_bin|sed "s/$/ /g"|grep -o "/[a-zA-Z/]+/bin/${python_bin} "
    return 0
}

function check_fabric_3
{
    local fab_version=`fab --version|grep -i "fabric3"`
    if [ ! -z "$fab_version" ];then
        echo = $fab_version
        return 0
    fi
    return 0
}


function check_docker
{
    local fab_version=`sudo docker --version|grep -i "docker"`
    if [ ! -z "$fab_version" ];then
        echo = $fab_version
        return 0
    fi
    return 0
}

function check_docker_compose
{
    local fab_version=`sudo docker-compose --version|grep -i "docker"`
    if [ ! -z "$fab_version" ];then
        echo = $fab_version
        return 0
    fi
    return 0
}


#check_python_3
#echo $?
#check_fabric_3
#echo $?
