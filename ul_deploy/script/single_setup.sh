#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e


host=
password=
conf_name_num=
unichain_conf_name=
rethinkdb=false
unichain=false

if [ $# -lt 3 ] ; then
    echo "host, password and conf_name_num should not be empty"
    exit 1
fi

while getopts "h:p:n:ru" arg
do
    case $arg in
        h)
            host=$OPTARG
            #echo "h's arg:$OPTARG"
            #host=user@ip
        ;;
        p)
            password=$OPTARG
            #echo "p's arg:$OPTARG"
        ;;
        n)
            conf_name_num=$OPTARG
            unichain_conf_name="bcdb_conf"${conf_name_num}
            #echo "n's arg:$OPTARG"
        ;;
        r)
            rethinkdb=true
        ;;
        u)
            unichain=true
        ;;

        ?)
            echo "Usage: single_setup -h user@host -p password -n num [-r] [-u]"
            exit 1
        ;;
    esac
done

# host, password and conf_name_num should not be empty
if [ "x${host}" == "x" -o "x${password}" == "x" -o "x${conf_name_num}" == "x" ] ; then
    echo "host, password and conf_name_num should not be empty"
    exit 1
fi

# unichain_conf_name exist ?
_unichain_conf_file="../conf/unichain_confiles/"${unichain_conf_name}
if [ ! -f "${_unichain_conf_file}" ] ; then
    echo "$_unichain_conf_file not eixst"
    exit 1
fi

hostandport=${host}":22"

# 2. install software
echo -e "[INFO]==========install base sofeware========="
fab set_node:$hostandport,password=$password install_base_software

echo -e "[INFO]==========install collectd========="
fab set_node:$hostandport,password=$password install_collectd

echo -e "[INFO]==========configure collectd=========="
fab set_node:$hostandport,password=$password configure_collectd

#rethinkdb install&configure
echo -e "[INFO]==========install  rethinkdb=========="
fab set_node:$hostandport,password=$password install_rethinkdb
echo -e "[INFO]==========configure  rethinkdb=========="
fab set_node:$hostandport,password=$password configure_rethinkdb

#localdb install
echo -e "[INFO]==========install localdb=========="
fab set_node:$hostandport,password=$password install_localdb

#init localdb ,init the data store dirs /data/localdb/{bigchain,votes,backlog}
fab set_node:$hostandport,password=$password init_localdb

#install unichain
CUR_INSTALL_PATH=$(cd "$(dirname "$0")"; pwd)
rm -f ${CUR_INSTALL_PATH}/unichain-archive.tar.gz 2>/dev/null

echo -e "[INFO]==========install unichain=========="
# install from local tar start
cd ../../
tar -cf unichain-archive.tar *
gzip unichain-archive.tar
mv unichain-archive.tar.gz ul_deploy/script/
cd -
fab set_node:$hostandport,password=$password install_unichain_from_git_archive
rm -f ${CUR_INSTALL_PATH}/unichain-archive.tar.gz 2>/dev/null
# install from local tar end

# configure unichain config
fab set_node:$hostandport,password=$password send_confile:$unichain_conf_name
exit 0
