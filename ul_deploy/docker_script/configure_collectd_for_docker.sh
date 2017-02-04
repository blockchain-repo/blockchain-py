#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

# (Re)create the Collectd configuration file conf/collectd.conf
echo -e "[INFO]==========init collectd conf========="
python3 create_collectd_conf.py

# Configure collectd.conf and restart
echo -e "[INFO]==========configure collectd=========="
fab configure_collectd_for_docker

exit 0
