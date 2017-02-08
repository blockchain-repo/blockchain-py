#! /bin/bash

source ./check_tools_util.sh

fab_version=`check_docker`
[ -z "$fab_version" ] && {
    echo -e "[WARNING]==========docker not exist,install begin=========="
    apt-get update
    curl -sSL http://acs-public-mirror.oss-cn-hangzhou.aliyuncs.com/docker-engine/resume | sh -
    echo -e "[WARNING]==========docker install end=========="
} || {
    echo -e "[WARNING]==========using $fab_version=========="
}


fab_version=`check_docker_compose`
[ -z "$fab_version" ] && {
    echo -e "[WARNING]==========docker-compose not exist,install begin=========="
    wget -O /usr/local/bin/docker-compose https://github.com/docker/compose/releases/download/1.8.0/docker-compose-`uname -s`-`uname -m`
    chmod +x /usr/local/bin/docker-compose
    echo -e "[WARNING]==========docker-compose install end=========="
} || {
    echo -e "[WARNING]==========using $fab_version=========="
}