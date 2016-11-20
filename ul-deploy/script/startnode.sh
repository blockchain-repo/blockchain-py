
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
		    echo "Usage: startnode -h user@host -p password [-r] [-u]"
		    exit 1
		    ;;
        esac
done

hostandport=${host}":22"

# start rethinkdb 
if [ $rethinkdb != false ]
then
    echo "start rethinkdb..."
    fab set_node:$hostandport,password=$password start_rethinkdb
fi

#start unichain
if [ $unichain != false ]
then
    echo "start unichain..."
    fab set_node:$hostandport,password=$password start_unichain
fi




