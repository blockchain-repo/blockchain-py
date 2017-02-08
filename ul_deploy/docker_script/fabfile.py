
# -*- coding: utf-8 -*-

"""A Fabric fabfile with functionality to prepare, install, and configure
BigchainDB, including its storage backend (RethinkDB).
"""

from __future__ import with_statement, unicode_literals

from os import environ  # a mapping (like a dict)
import sys
import os
from fabric.api import sudo,cd, env, hosts, local
from fabric.api import task, parallel
from fabric.contrib.files import sed
from fabric.operations import run, put, get
from fabric.context_managers import settings

import json
from hostlist import public_dns_names,public_hosts,public_pwds,public_host_pwds

################################ Fabric Initial Config Data  ######################################

env['passwords'] = public_host_pwds
env['hosts']=env['passwords'].keys()


@task
@parallel
def clear_all_nodes():
    with settings(warn_only=True):
        #sudo('docker stop $(sudo docker ps -q)')
        #sudo('docker rm $(sudo docker ps -a -q)')
        #sudo('docker rmi $(sudo docker images -q)')
        sudo('rm -rf /uni_docker/* 2>/dev/null')
        sudo('mkdir -p /uni_docker/rethinkdb')
        sudo('mkdir -p /uni_docker/localdb')
        sudo('mkdir -p /uni_docker/collectd')
        sudo('mkdir -p /uni_docker/docker_images')
        sudo('mkdir -p /uni_docker/docker_images_bak')
        sudo("chown -R " + env.user + ':' + env.user + ' /uni_docker')
        sudo("chown -R " + env.user + ':' + env.user + ' /uni_docker/docker_images')
        sudo("chown -R " + env.user + ':' + env.user + ' /uni_docker/docker_images_bak')

@task
@parallel
def init_all_nodes():
    with settings(warn_only=True):
        #sudo('docker stop $(sudo docker ps -q)')
        #sudo('docker rm $(sudo docker ps -a -q)')
        #sudo('docker rmi $(sudo docker images -q)')
        sudo('mkdir -p /uni_docker/rethinkdb')
        sudo('mkdir -p /uni_docker/localdb')
        sudo('mkdir -p /uni_docker/collectd')
        sudo('mkdir -p /uni_docker/docker_images')
        sudo('mkdir -p /uni_docker/docker_images_bak')
        sudo("chown -R " + env.user + ':' + env.user + ' /uni_docker')


@task
@parallel
def clear_all_docker_images():
    with settings(warn_only=True):
        sudo('docker stop $(sudo docker ps -q)')
        sudo('docker rm $(sudo docker ps -a -q)')
        sudo('docker rmi $(sudo docker images -q)')

@task
@parallel
def clear_unichain_docker_images():
    with settings(warn_only=True):
        sudo('docker stop $(sudo docker ps -q)')
        sudo('docker rm $(sudo docker ps -a -q)')
        sudo('docker rmi unichain_bdb')

@task
@parallel
def clear_rethinkdb_docker_images():
    with settings(warn_only=True):
        sudo('docker stop $(sudo docker ps -q)')
        sudo('docker rm $(sudo docker ps -a -q)')
        sudo('docker rmi rethinkdb')

############################### Docker related ######################################

@task
@parallel
def run_init_docker_env():
    with settings(warn_only=True):
        status = os.system('./run_init_docker_env.sh')

# Install docker
@task
@parallel
def install_docker():
    with settings(warn_only=True):
        sudo("echo deb http://mirrors.aliyun.com/docker-engine/apt/repo ubuntu-trusty main > /etc/apt/sources.list.d/docker.list")
        sudo("apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D")
        sudo("apt-get update")
        sudo("apt-get install -y")
        sudo("apt-get install -y docker-engine")
        sudo("wget -O /usr/local/bin/docker-compose https://github.com/docker/compose/releases/download/1.8.0/docker-compose-`uname -s`-`uname -m`")
        sudo('chmod +x /usr/local/bin/docker-compose')

# Install docker
@task
@parallel
def install_docker2():
    with settings(warn_only=True):
        sudo("apt-get update")
        sudo("curl -sSL http://acs-public-mirror.oss-cn-hangzhou.aliyuncs.com/docker-engine/internet | sh -")
        sudo("wget -O /usr/local/bin/docker-compose https://github.com/docker/compose/releases/download/1.8.0/docker-compose-`uname -s`-`uname -m`")
        sudo('chmod +x /usr/local/bin/docker-compose')

@task
def check_docker():
    with settings(warn_only=True):
        version = sudo('docker --version|grep -i "docker"',shell=True)
        print(version)
        print(version)
        if version==None:
            print("00000")
        else:
            print("1111")

# DON'T PUT @parallel
@task
def set_host(host_index):
    """A helper task to change env.hosts from the
    command line. It will only "stick" for the duration
    of the fab command that called it.

    Args:
        host_index (int): 0, 1, 2, 3, etc.
    Example:
        fab set_host:4 fab_task_A fab_task_B
        will set env.hosts = [public_dns_names[4]]
        but only for doing fab_task_A and fab_task_B
    """
    env.hosts = [public_dns_names[int(host_index)]]
    env.password = [public_pwds[int(host_index)]]


# Send the specified configuration file to
# the remote host and save it there in
# /uni_docker/.unichain
# Use in conjunction with set_host()
# No @parallel
@task
def send_unichain_confile_for_docker(confile):
    with settings(warn_only=True):
        if run("test -d /uni_docker").failed:
            sudo("mkdir /uni_docker")
            sudo("chown -R " + env.user + ':' + env.user + ' /uni_docker')
        put('../conf/unichain_confiles/' + confile,
            '/uni_docker/.unichain',
            mode=0x0600,
            use_sudo=True)

# Configure RethinkDB
@task
def send_rethinkdb_configure_for_docker():
    """Confiure of RethinkDB"""
    with settings(warn_only=True):
        if run("test -d /uni_docker/rethinkdb").failed:
            sudo("mkdir /uni_docker/rethinkdb")
            sudo("chown -R " + env.user + ':' + env.user + ' /uni_docker')
        # copy config file to target system
        put('../conf/rethinkdb.conf',
            '/uni_docker/rethinkdb/default.conf',
            mode=0x0600,
            use_sudo=True)

# Configure Collectd
@task
def configure_collectd_for_docker():
    """Confiure of Collectd"""
    with settings(warn_only=True):
        # fix: lib version too high
        sudo('ln -sf /lib/x86_64-linux-gnu/libudev.so.?.?.? /lib/x86_64-linux-gnu/libudev.so.0')
        sudo('ldconfig')
        # copy config file to target system
        put('../conf/collectd.conf','/uni_docker/collectd/collectd.conf',mode=0x0600,use_sudo=True)
        # update by  mayx, op at start_all
        # finally restart instance
        # sudo('service collectd restart', pty=False)

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


# Load docker image
@task
@parallel
def load_images():
    with settings(warn_only=True):
        if run("test -d /uni_docker/docker_images").failed:
            sudo("mkdir /uni_docker/docker_images")
        if run("test -d /uni_docker/docker_images_bak").failed:
            sudo("mkdir /uni_docker/docker_images_bak")

        sudo("rm -rf /uni_docker/docker_images_bak/*")
        sudo("mv /uni_docker/docker_images/* /uni_docker/docker_images_bak")
        sudo("rm -rf /uni_docker/docker_images/*")

        put('../docker_images/rethinkdb.tar', '/uni_docker/docker_images/rethinkdb.tar', mode=0x0600, use_sudo=True)
        put('../docker_images/unichain.tar', '/uni_docker/docker_images/unichain.tar', mode=0x0600, use_sudo=True)
        with cd('/uni_docker/docker_images'):
            # todo: remove existed file
            # sudo("wget http://ofbwpkkls.bkt.clouddn.com/unichain.tar.gz")
            sudo('docker load < /uni_docker/docker_images/rethinkdb.tar')
            sudo('docker load < /uni_docker/docker_images/unichain.tar')
            #sudo("wget http://ofbwpkkls.bkt.clouddn.com/docker-compose.yml")
            sudo('rm -f docker-compose.yml')
        put('../../docker-compose.yml', '/uni_docker/docker_images/docker-compose.yml', mode=0x0600, use_sudo=True)

# Load docker image
@task
@parallel
def update_unichain_images():
    with settings(warn_only=True):
        if run("test -d /uni_docker/docker_images").failed:
            sudo("mkdir /uni_docker/docker_images")
        if run("test -d /uni_docker/docker_images_bak").failed:
            sudo("mkdir /uni_docker/docker_images_bak")

        sudo("rm -rf /uni_docker/docker_images_bak/unichain.tar")
        sudo("mv /uni_docker/docker_images/unichain.tar /uni_docker/docker_images_bak")
        sudo("rm -rf /uni_docker/docker_images/unichain.tar")
        put('../docker_images/unichain.tar', '/uni_docker/docker_images/unichain.tar', mode=0x0600, use_sudo=True)
        with cd('/uni_docker/docker_images'):
            # sudo("wget http://ofbwpkkls.bkt.clouddn.com/unichain.tar.gz")
            sudo('docker load < /uni_docker/docker_images/unichain.tar')
            # sudo("wget http://ofbwpkkls.bkt.clouddn.com/docker-compose.yml")
            sudo('rm -f docker-compose.yml')
        put('../../docker-compose.yml', '/uni_docker/docker_images/docker-compose.yml', mode=0x0600, use_sudo=True)

# Load docker image
@task
@parallel
def update_rethinkdb_images():
    with settings(warn_only=True):
        if run("test -d /uni_docker/docker_images").failed:
            sudo("mkdir /uni_docker/docker_images")
        if run("test -d /uni_docker/docker_images_bak").failed:
            sudo("mkdir /uni_docker/docker_images_bak")

        sudo("rm -rf /uni_docker/docker_images_bak/rethinkdb.tar")
        sudo("mv /uni_docker/docker_images/rethinkdb.tar /uni_docker/docker_images_bak")
        sudo("rm -rf /uni_docker/docker_images/rethinkdb.tar")
        put('../docker_images/rethinkdb.tar', '/uni_docker/docker_images/rethinkdb.tar', mode=0x0600, use_sudo=True)
        with cd('/uni_docker/docker_images'):
            # todo: remove existed file
            # sudo("wget http://ofbwpkkls.bkt.clouddn.com/unichain.tar.gz")
            sudo('docker load < /uni_docker/docker_images/rethinkdb.tar')
            # sudo("wget http://ofbwpkkls.bkt.clouddn.com/docker-compose.yml")
            sudo('rm -f docker-compose.yml')
        put('../../docker-compose.yml', '/uni_docker/docker_images/docker-compose.yml', mode=0x0600, use_sudo=True)


# Up docker container
@task
@parallel
def start_docker():
    with settings(warn_only=True):
        with cd('/uni_docker/docker_images'):
            sudo("docker-compose up")

# Up docker container
@task
@parallel
def start_docker_rdb():
    with settings(warn_only=True):
        with cd('/uni_docker/docker_images'):
            sudo("docker-compose up -d rdb")

# As db has already been inited, no problem to start bdb at the same time
@task
@parallel
def start_docker_bdb(num_shards=len(public_dns_names), num_replicas=(int(len(public_dns_names)/2)+1)):
    with settings(warn_only=True):
        with cd('/uni_docker/docker_images'):
            sudo("NUM_SHARDS={} NUM_REPLICAS={} docker-compose up -d bdb".format(num_shards, num_replicas))

# Init database and set shards/replicas
@task
@hosts(public_dns_names[0])
def start_docker_bdb_init(num_shards=len(public_dns_names), num_replicas=(int(len(public_dns_names)/2)+1)):
    with settings(warn_only=True):
        with cd('/uni_docker/docker_images'):
            sudo("NUM_SHARDS={} NUM_REPLICAS={} docker-compose up -d bdb_init".format(num_shards, num_replicas))






#########################bak conf task#########################
@task
@parallel
def bak_rethinkdb_conf(base):
    with settings(warn_only=True):
        get('/uni_docker/rethinkdb/default.conf', '%s/rethinkdb/default.conf_%s_%s' % (base, env.user, env.host), use_sudo=True)

@task
@parallel
def bak_collected_conf(base):
    with settings(warn_only=True):
        get('/uni_docker/collectd/collectd.conf', ' %s/collected/collected.conf_%s_%s' % (base, env.user, env.host), use_sudo=True)

@task
@parallel
def bak_unichain_conf(base):
    with settings(warn_only=True):
        get('/uni_docker/.unichain', '%s/unichain/unichain_%s_%s' % (base, env.user, env.host), use_sudo=True)

