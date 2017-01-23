from fabric.api import sudo,cd, env, hosts
from fabric.api import task, parallel
from fabric.contrib.files import sed
from fabric.operations import run, put, get
from fabric.context_managers import settings

import json
from hostlist import public_dns_names,public_hosts,public_pwds,public_host_pwds

@task
@parallel
def clear_all_nodes(base):
    with settings(warn_only=True):
        sudo('docker stop $(sudo docker ps -q)')
        sudo('docker rm $(sudo docker ps -a -q)')
        sudo('docker rmi $(sudo docker images -q)')
        sudo('rm -rf /data/rethinkdb/* 2>/dev/null')
        sudo('rm -rf /data/localdb/* 2>/dev/null')
        sudo('mkdir /data/rethinkdb')
        sudo('mkdir /data/localdb')

#########################bak conf task#########################
@task
@parallel
def bak_rethinkdb_conf(base):
    with settings(warn_only=True):
        get('/etc/rethinkdb/instances.d/default.conf', '%s/rethinkdb/default.conf_%s_%s' % (base, env.user, env.host), use_sudo=True)

@task
@parallel
def bak_collected_conf(base):
    with settings(warn_only=True):
        get('/etc/collectd/collectd.conf', ' %s/collected/collected.conf_%s_%s' % (base, env.user, env.host), use_sudo=True)

@task
@parallel
def bak_unichain_conf(base):
    with settings(warn_only=True):
        get('~/.unichain', '%s/unichain/unichain_%s_%s' % (base, env.user, env.host), use_sudo=True)


############################### Docker related ######################################
# Install docker
@task
@parallel
def install_docker():
    with settings(warn_only=True):
        sudo("echo deb https://apt.dockerproject.org/repo ubuntu-trusty main > /etc/apt/sources.list.d/docker.list")
        sudo("apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D")
        sudo("apt-get update")
        sudo("apt-get install -y --force-yes docker-engine")
        sudo("wget -O /usr/local/bin/docker-compose https://github.com/docker/compose/releases/download/1.8.0/docker-compose-`uname -s`-`uname -m`")
        sudo('chmod +x /usr/local/bin/docker-compose')

# Load docker image
@task
@parallel
def load_image():
    with settings(warn_only=True):
        if run("test -d ~/docker").failed:
            sudo("mkdir ~/docker")
        with cd('~/docker'):
            # todo: remove existed file
            sudo("wget http://ofbwpkkls.bkt.clouddn.com/unichain.tar.gz")
            sudo("tar zxvf unichain.tar.gz")
            sudo('docker load < unichain.tar')
            #sudo("wget http://ofbwpkkls.bkt.clouddn.com/docker-compose.yml")
            sudo('rm -f docker-compose.yml')
        put('../../docker-compose.yml', '~/docker/docker-compose.yml', mode=0x0600, use_sudo=True)

# Up docker container
@task
@parallel
def start_docker():
    with settings(warn_only=True):
        with cd('~/docker'):
            sudo("docker-compose up")

# Send the specified configuration file to
# the remote host and save it there in
# /uni_docker/.unichain
# Use in conjunction with set_host()
# No @parallel
@task
def send_confile_for_docker(confile):
    with settings(warn_only=True):
        if run("test -d /uni_docker").failed:
            sudo("mkdir /uni_docker")
            sudo("chown -R " + env.user + ':' + env.user + ' /uni_docker')
        put('../conf/unichain_confiles/' + confile,
            '/uni_docker/.unichain')

# Configure RethinkDB
@task
@parallel
def configure_rethinkdb_for_docker():
    """Confiure of RethinkDB"""
    with settings(warn_only=True):
        if run("test -d /uni_docker").failed:
            sudo("mkdir /uni_docker")
            sudo("chown -R " + env.user + ':' + env.user + ' /uni_docker')
        # copy config file to target system
        put('../conf/rethinkdb.conf',
            '/uni_docker/default.conf')

# Stop and remove all containers
@task
@parallel
def remove_all_docker_containers():
    sudo("docker rm -f $(docker ps -a -q)")

# Remove rethinkdb data and configs
@task
@parallel
def remove_all_docker_data():
    sudo("rm -rf /uni_docker/rethinkdb_data")

# Up docker container
@task
@parallel
def start_docker_rdb():
    with settings(warn_only=True):
        with cd('~/docker'):
            sudo("docker-compose up -d rdb")

# As db has already been inited, no problem to start bdb at the same time
@task
@parallel
def start_docker_bdb():
    with settings(warn_only=True):
        with cd('~/docker'):
            sudo("docker-compose up -d bdb")

# Init database and set shards/replicas
@task
@hosts(public_dns_names[0])
def start_docker_bdb_init(num_shards=len(public_dns_names), num_replicas=(int(len(public_dns_names)/2)+1)):
    with settings(warn_only=True):
        with cd('~/docker'):
            sudo("NUM_SHARDS={} NUM_REPLICAS={} docker-compose up -d bdb_init".format(num_shards, num_replicas))
