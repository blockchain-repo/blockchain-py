#! /bin/bash

host=
password=
rethinkdb=false
unichain=false

while getopts "h:p:ru" arg
do
    case $arg in
        h)
            host=$OPTARG
            #echo "h's arg:$OPTARG"
        ;;
        p)
            password=$OPTARG
        #echo "p's arg:$OPTARG"
        ;;
        r)
            rethinkdb=true
        ;;
        u)
            unichain=true
        ;;
        ?) 
            echo "Usage: stopnode -h user@host -p password [-r] [-u]"
            exit 1
        ;;
    esac
done

hostandport=${host}":22"

# stop  unichain
if [ $unichain != false ]
then
    echo -e "[INFO]==========stop unichain[$hostandport]...=========="
    fab set_node:$hostandport,password=$password stop_unichain_api
    fab set_node:$hostandport,password=$password stop_unichain
fi

# stop rethinkdb 
if [ $rethinkdb != false ]
then
    echo -e "[INFO]==========stop rethinkdb[$hostandport]...=========="
    fab set_node:$hostandport,password=$password stop_rethinkdb
fi
