#! /bin/bash

if [ $# != 1 ]
then
   echo "Usage: ./clustercontrol.sh start|stop "
   exit 1
fi

# start or stop cluster
if [ $1 == "start" ]
then
   echo -e "[INFO]==========start cluster rethinkdb...=========="
   fab start_rethinkdb
   echo -e "[INFO]==========start cluster unichain...=========="
   fab start_unichain
elif [ $1 == "stop" ]
then
   echo -e "[INFO]=========stop cluster unichain...=========="
   fab stop_unichain
   echo -e "[INFO]==========stop cluster rethinkdb...=========="
   fab stop_rethinkdb
fi

exit 0
