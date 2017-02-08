#! /bin/bash

source ./check_tools_util.sh

docker_version=`check_docker`
[ -z "$docker_version" ] && {
    echo -e "[WARNING]==========docker not exist,install begin=========="
    sudo apt-get update
    sudo curl -sSL http://acs-public-mirror.oss-cn-hangzhou.aliyuncs.com/docker-engine/resume | sh -
    echo -e "[WARNING]==========docker install end=========="
} || {
    echo -e "[WARNING]==========using $docker_version=========="
}


docker_compose=`check_docker_compose`
[ -z "$docker_compose" ] && {
    echo -e "[WARNING]==========docker-compose not exist,install begin=========="
    sudo wget -O /usr/local/bin/docker-compose https://github.com/docker/compose/releases/download/1.8.0/docker-compose-`uname -s`-`uname -m`
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "[WARNING]==========docker-compose install end=========="
} || {
    echo -e "[WARNING]==========using $docker_compose=========="
}
