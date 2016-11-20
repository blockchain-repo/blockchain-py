#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

function printErr()
    {
        echo "usage: ./configure_unichain.sh <number_of_files>"
        echo "No argument $1 supplied"
    }

if [ -z "$1" ]; then
    printErr "<number_of_files>"
    exit 1
fi

CONFDIR=../conf/unichain_confiles
NUMFILES=$1

# If $CONFDIR exists, remove it
if [ -d "$CONFDIR" ]; then
    rm -rf $CONFDIR
fi

# Create $CONFDIR
mkdir $CONFDIR

# Use the unichain configure command to create
# $NUMFILES BigchainDB config files in $CONFDIR
for (( i=0; i<$NUMFILES; i++ )); do
    CONPATH=$CONFDIR"/bcdb_conf"$i
    echo "Writing "$CONPATH
    unichain -y -c $CONPATH configure
done


num_pairs=$1
NUM_NODES=$1

python3 write_keypairs_file.py $num_pairs
python3 clusterize_confiles.py -k $CONFDIR $NUM_NODES

# Send one of the config files to each instance
for (( HOST=0 ; HOST<$NUM_NODES ; HOST++ )); do
    CONFILE="bcdb_conf"$HOST
    echo "Sending "$CONFILE
    fab set_host:$HOST send_confile:$CONFILE
done
