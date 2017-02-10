#!/bin/bash

#Args: $1 => date_str
function init_bak_images_dir()
{
    local date_str=$1
    sudo mkdir -p /unichain_docker/unichain_image_back/${date_str}
    sudo mkdir -p /unichain_docker/rethinkdb_image_back/${date_str}
    return 0
}


date_str=`date +"%Y%m%d%H%M%S"`

init_bak_images_dir ${date_str}

bak_unichain_base_path=/unichain_docker/unichain_image_back/${date_str}
bak_rethinkdb_base_path=/unichain_docker/rethinkdb_image_back/${date_str}

fab bak_unichain_docker_images:"${bak_unichain_base_path}"
fab bak_rethinkdb_docker_images:"${bak_rethinkdb_base_path}"



