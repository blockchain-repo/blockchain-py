#!/bin/bash

set -e

#detect rethinkdb
# get port & check port & check process
echo -e "[INFO]===========detect rethinkdb==========="
fab detect_rethinkdb

#detect localdb
# get port & check port & check process
echo -e "[INFO]===========detect localdb==========="
fab detect_localdb

#detect unichain-pro
# get bigchain port & check port & check process
echo -e "[INFO]===========detect unichain-pro==========="
fab detect_unichain_pro

#detect unichain-api
# get api port & check port & check api
echo -e "[INFO]===========detect unichain-api==========="
fab detect_unichain_api

exit 0
