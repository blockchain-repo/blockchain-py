#! /bin/bash

if [ $# != 1 ]
then
   echo "Usage: ./clustercontrol.sh start|stop "
   exit 1
fi

# no matter start or stop cluster, the unichain_restore api must be stop
# the api share the localdb dirs and must be single process!
echo -e "[INFO]=========stop cluster unichain_restore...=========="
fab stop_unichain_restore

# start or stop cluster
if [ $1 == "start" ]
then
   echo -e "[INFO]==========start cluster rethinkdb...=========="
   fab start_rethinkdb
   echo -e "[INFO]==========start cluster unichain...=========="
   fab start_unichain
elif [ $1 == "stop" ]
then
   echo -e "[INFO]=========stop cluster python...=========="
   fab stop_python
   echo -e "[INFO]=========stop cluster unichain...=========="
   fab stop_unichain
   echo -e "[INFO]==========stop cluster rethinkdb...=========="
   fab stop_rethinkdb
fi

exit 0
