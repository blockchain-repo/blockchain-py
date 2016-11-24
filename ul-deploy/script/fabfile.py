
# -*- coding: utf-8 -*-

"""A Fabric fabfile with functionality to prepare, install, and configure
BigchainDB, including its storage backend (RethinkDB).
"""

from __future__ import with_statement, unicode_literals

from os import environ  # a mapping (like a dict)
import sys

from fabric.api import sudo, env, hosts
from fabric.api import task, parallel
from fabric.contrib.files import sed
from fabric.operations import run, put
from fabric.context_managers import settings

from hostlist import public_dns_names as public_hosts,public_pwds,public_host_pwds


################################ Fabric Initial Config Data  ######################################

env['passwords'] = public_host_pwds
env['hosts']=env['passwords'].keys()

################################ Check envl  ######################################
#step:check port&process&data,conf path
@task
def check_rethinkdb():
    with settings(warn_only=True):
        #TODO:
        pass

#step:check port&process&data,conf path
@task
def check_localdb():
    with settings(warn_only=True):
        #TODO:
        pass

#step:check port&process&data,conf path
@task
def check_unichain_pro():
    with settings(warn_only=True):
        #TODO:
        pass

################################ First Install  ######################################
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
        will set env.hosts = [public_hosts[4]]
        but only for doing fab_task_A and fab_task_B
    """
    env.hosts = [public_hosts[int(host_index)]]
    env.password = [public_pwds[int(host_index)]]

# Install base software
@task
@parallel
def install_base_software():
    # python pip3 :
    with settings(warn_only=True):
        sudo('apt-get -y update')
        sudo('dpkg --configure -a')
        sudo('apt-get -y -f install')
        sudo('apt-get -y install git gcc g++ python3-dev libffi-dev python3-setuptools python3-pip ntp screen')
        sudo('pip3 install --upgrade pip')
        sudo('pip3 install --upgrade setuptools')
        sudo('pip3 --version')

# Install Collectd
@task
@parallel
def install_collectd():
    """Installation of Collectd"""
    with settings(warn_only=True):
        sudo("echo 'collectd install' ")
        sudo("echo 'deb http://http.debian.net/debian wheezy-backports-sloppy main contrib non-free' | sudo tee /etc/apt/sources.list.d/backports.list")
        sudo("apt-get update")
        sudo("apt-get install -y --force-yes -t wheezy-backports-sloppy collectd")


# Configure Collectd
@task
@parallel
def configure_collectd():
    """Confiure of Collectd"""
    with settings(warn_only=True):
        # fix: lib version too high
        sudo('ln -sf /lib/x86_64-linux-gnu/libudev.so.?.?.? /lib/x86_64-linux-gnu/libudev.so.0')
        sudo('ldconfig')
        # copy config file to target system
        put('../conf/collectd.conf',
            '/etc/collectd/collectd.conf',
            mode=0x0600,
            use_sudo=True)
        # finally restart instance
        sudo('service collectd restart', pty=False)


@task
@parallel
def start_collectd():
    """Installation of Collectd"""
    with settings(warn_only=True):
        sudo("echo 'collectd restart' ")
        sudo('service collectd restart', pty=False)


# @task
# @parallel
# def stop_collectd():
#     """Installation of Collectd"""
#     with settings(warn_only=True):
#         sudo("echo 'collectd stop' ")
#         sudo('service collectd stop', pty=False)


# Install RethinkDB
@task
@parallel
def install_rethinkdb():
    with settings(warn_only=True):
        sudo("mkdir -p /data/rethinkdb")
        # install rethinkdb
        sudo("echo 'deb http://download.rethinkdb.com/apt trusty main' | sudo tee /etc/apt/sources.list.d/rethinkdb.list")
        sudo("wget -qO- http://download.rethinkdb.com/apt/pubkey.gpg | sudo apt-key add -")
        sudo("apt-get update")
        sudo("apt-get -y install rethinkdb")
        # initialize rethinkdb data-dir
        sudo('rm -rf /data/rethinkdb/*')


# Configure RethinkDB
@task
@parallel
def configure_rethinkdb():
    """Confiure of RethinkDB"""
    with settings(warn_only=True):
        # copy config file to target system
        put('../conf/rethinkdb.conf',
            '/etc/rethinkdb/instances.d/default.conf',
            mode=0x0600,
            use_sudo=True)
        # finally restart instance
        sudo('/etc/init.d/rethinkdb restart')


# Send the specified configuration file to
# the remote host and save it there in
# ~/.unichain
# Use in conjunction with set_host()
# No @parallel
@task
def send_confile(confile):
    put('../conf/unichain_confiles/' + confile, 'tempfile')
    run('mv tempfile ~/.unichain')
    print('For this node, unichain show-config says:')
    run('unichain show-config')


# Install BigchainDB from a Git archive file
# named unichain-archive.tar.gz
@task
@parallel
def install_unichain_from_git_archive():
    put('../unichain-archive.tar.gz')
    user_group = env.user
    with settings(warn_only=True):
        if run("test -d ./unichain").failed:
            run("echo 'create unichain directory' ")
            run("mkdir -p ./unichain")
            sudo("chown -R " + user_group + ':' + user_group + ' ./unichain')
        else:
            run("echo 'remove old unichain directory' ")
            sudo("rm -rf ./unichain/*")
    with cd('~/unichain'):
        run('tar xvfz ../unichain-archive.tar.gz >/dev/null 2>&1')
        sudo('pip3 install -i http://pypi.douban.com/simple --upgrade setuptools')
        sudo('python3 setup.py install')
    sudo('rm unichain-archive.tar.gz')
    run('echo install_unichain_from_git_archive done!')

# install localdb
@task
@parallel
def install_localdb():
    # leveldb & plyvel install
    with settings(warn_only=True):
        user_group = env.user
        sudo("echo 'leveldb & plyvel install' ")
        sudo('rm -rf /data/localdb/*')
        sudo("mkdir -p /data/localdb/{bigchain,votes,header}")
        sudo("chown -R " + user_group + ':' + user_group + ' /data/localdb')
        sudo('pip3 install leveldb==0.194')
        sudo('apt-get install libleveldb1 libleveldb-dev libsnappy1 libsnappy-dev')
        sudo('apt-get -y -f install')
        sudo('pip3 install plyvel==0.9')


@task
@parallel
def init_localdb():
    with settings(warn_only=True):
        user_group = env.user
        sudo('rm -rf /data/localdb/*')
        sudo("echo init localdb")
        sudo("mkdir -p /data/localdb/{bigchain,votes,header}")
        sudo("chown -R " + user_group + ':' + user_group + ' /data/localdb')


# @task
# @parallel
# def install_rabbitmq():
#     # leveldb & plyvel install
#     with settings(warn_only=True):
#         # ramq & pika install
#         sudo(" echo 'ramq & pika install' ")
#         sudo('apt-get -y install rabbitmq-server')
#         sudo('pip3 install pika==0.10.0')
#         #sudo('rabbitmq-server restart')


################################### Base OP  ######################################
# unichain
# uninstall old unichain
@task
@parallel
def uninstall_unichain():
    with settings(warn_only=True):
        sudo("echo 'uninstall unichain app in usr/local/bin' ")
        sudo('rm /usr/local/bin/unichain')
        sudo('rm -rf /usr/local/lib/python3.4/dist-packages/BigchainDB-*')
        sudo('rm -rf ~/unichain')


# Initialize BigchainDB
# i.e. create the database, the tables,
# the indexes, and the genesis block.
# (The @hosts decorator is used to make this
# task run on only one node. See http://tinyurl.com/h9qqf3t )
@task
@hosts(public_hosts[0])
def init_unichain():
    with settings(warn_only=True):
        run('unichain -y drop',pty=False)
        run('unichain init', pty=False)


# Configure BigchainDB
@task
@parallel
def configure_unichain():
    run('unichain -y configure', pty=False)


@task
@hosts(public_hosts[0])
def drop_unichain():
    with settings(warn_only=True):
        run('unichain -y drop', pty=False)


# Set the number of shards (tables[bigchain,votes,backlog])
@task
@hosts(public_hosts[0])
def set_shards(num_shards=len(public_hosts)):
    # num_shards = len(public_hosts)
    run('unichain set-shards {}'.format(num_shards))


# Set the number of replicas (tables[bigchain,votes,backlog])
@task
@hosts(public_hosts[0])
def set_replicas(num_replicas):
    run('unichain set-replicas {}'.format(num_replicas))


# unichain
@task
@parallel
def start_unichain():
    with settings(warn_only=True):
        sudo('screen -d -m unichain -y start &', pty=False, user=env.user)


@task
@parallel
def stop_unichain():
    with settings(warn_only=True):
        # sudo("kill `ps -ef|grep unichain | grep -v grep|awk '{print $2}'` ")
        sudo("killall -9 unichain")


@task
@parallel
def restart_unichain():
    with settings(warn_only=True):
        sudo("killall -9 unichain")
        sudo('screen -d -m unichain -y start &', pty=False, user=env.user)


@task
@parallel
def start_unichain_load():
    sudo('screen -d -m unichain load &', pty=False)


# rethinkdb
# delete the disk data for rethinkdb in /data/rethinkdb/*
@task
@parallel
def clear_rethinkdb_data():
    with settings(warn_only=True):
        sudo("echo clean rethinkdb data")
        sudo('rm -rf /data/rethinkdb/*')


@task
def start_rethinkdb():
    sudo("service rethinkdb  start")


@task
def stop_rethinkdb():
    sudo("service rethinkdb stop")


@task
def restart_rethinkdb():
    sudo("service rethinkdb restart")


@task
def rebuild_rethinkdb():
    sudo("service rethinkdb index-rebuild -n 2")


########################### Node control ####################################
#set on node
@task
@parallel
def set_node(host,password):
    env['passwords'][host]=password
    env['hosts']=env['passwords'].keys()



################################################################
# Security / Firewall Stuff
################################################################

@task
def harden_sshd():
    """Security harden sshd.
    """
    # Disable password authentication
    sed('/etc/ssh/sshd_config',
        '#PasswordAuthentication yes',
        'PasswordAuthentication no',
        use_sudo=True)
    # Deny root login
    sed('/etc/ssh/sshd_config',
        'PermitRootLogin yes',
        'PermitRootLogin no',
        use_sudo=True)


@task
def disable_root_login():
    """Disable `root` login for even more security. Access to `root` account
    is now possible by first connecting with your dedicated maintenance
    account and then running ``sudo su -``.
    """
    sudo('passwd --lock root')


@task
def set_fw():
    # snmp
    sudo('iptables -A INPUT -p tcp --dport 161 -j ACCEPT')
    sudo('iptables -A INPUT -p udp --dport 161 -j ACCEPT')
    # dns
    sudo('iptables -A OUTPUT -p udp -o eth0 --dport 53 -j ACCEPT')
    sudo('iptables -A INPUT -p udp -i eth0 --sport 53 -j ACCEPT')
    # rethinkdb
    sudo('iptables -A INPUT -p tcp --dport 28015 -j ACCEPT')
    sudo('iptables -A INPUT -p udp --dport 28015 -j ACCEPT')
    sudo('iptables -A INPUT -p tcp --dport 29015 -j ACCEPT')
    sudo('iptables -A INPUT -p udp --dport 29015 -j ACCEPT')
    sudo('iptables -A INPUT -p tcp --dport 8080 -j ACCEPT')
    sudo('iptables -A INPUT -i eth0 -p tcp --dport 8080 -j DROP')
    sudo('iptables -I INPUT -i eth0 -s 127.0.0.1 -p tcp --dport 8080 -j ACCEPT')
    # save rules
    sudo('iptables-save >  /etc/sysconfig/iptables')




################################### Other OP #######################################
#count the special process count
@task
@parallel
def count_process_by_name(name):
    with settings(warn_only=True):
        if name is not None:
            user = env.user
            cmd = "echo '{}`s {} process counts is ' `ps -e |grep {} | wc -l`".format(user,name,name)
            sudo("echo {}".format(cmd) )
            sudo(cmd)


@task
@parallel
def init_all_nodes():
    with settings(warn_only=True):
        sudo('killall -9 unichain')
        sudo('killall -9 rethinkdb')
        # sudo('pip3 uninstall unichain')
        sudo('rm -rf /data/rethinkdb/*')
        sudo('rm -rf /data/localdb/*')


@task
@parallel
def kill_all_nodes():
    with settings(warn_only=True):
        sudo('killall -9 rethinkdb')
        sudo('killall -9 unichain')


@task
@parallel
def kill_process_with_name(name):
    with settings(warn_only=True):
        if name is not None:
            sudo("echo kill process use the name %s" %(name))
            sudo("killall -9 {}".format(name))


@task
@parallel
def kill_process_with_port(port):
    with settings(warn_only=True):
        sudo("echo kill process use the port %s" %(port))
        sudo("killall -9 `netstat -nlp | grep :{} | awk '{print $7}' | awk -F'/' '{ print $1 }'`".format(port))

@task
@parallel
def reboot_all_hosts():
    with settings(warn_only=True):
        user = env.user
        host = env.host
        sudo("will reboot the host: {}, user: {}".format(host,user))
        sudo("reboot")


@task
@parallel
def write_rethinkdb_join(port=29015):
    with settings(warn_only=True):
        if port is None:
            port = 29015
        join_infos =""
        rethinkdb_conf_path = "/etc/rethinkdb/instances.d/default.conf"
        for host in env['hosts']:
            join_info = "join={}:{}".format(host,port)
            join_infos += join_info + "\\n"
            sudo("echo {} {}".format(host,join_info))
        join_infos =join_infos[:-2]
        sudo("echo 'The joins will write to {}:\n{}'".format(rethinkdb_conf_path,join_infos))
        if join_infos != '':
           sudo("sed -i '$a {}' /etc/rethinkdb/instances.d/default.conf".format(join_infos))


@task
@parallel
def remove_rethinkdb_join():
    with settings(warn_only=True):
         sudo("sed -i /join=19/d /etc/rethinkdb/instances.d/default.conf")


@task
@parallel
def seek_rethinkdb_join():
    with settings(warn_only=True):
         sudo("sed -n /join=19/p /etc/rethinkdb/instances.d/default.conf")


@task
@parallel
def start_unichain_load_processes_counts(m=1,c=None):
    sudo("echo " + 'm={} c={} &'.format(m, c))
    if m is None and c is None:
        sudo('screen -d -m unichain_ load &', pty=False,user=env.user)
    flag = ''
    v = None
    if m :
        flag=flag+'m'
        v = m
    if c :
        flag=flag+'c'
        v = c
    if len(flag) == 1:
        cmd = 'screen -d -m unichain_ load -{} {} &'.format(flag, v)
        sudo(cmd, pty=False,user=env.user)
        sudo("echo {}".format(cmd) )

    if len(flag) == 2:
        cmd = 'screen -d -m unichain_ load -m {} -c {} &'.format(m, c)
        sudo(cmd, pty=False,user=env.user)
        sudo("echo {}".format(cmd))


@task
@parallel
def test_nodes_rethinkdb(file=1,num=1,blank=False):
    with settings(warn_only=True):
       user = env.user
       py_path1 = '/home/' + user + '/simplechaindb/clusterdeploy/rethinkdb-tests/rethindbTest01.py' #multi process
       py_path2 = '/home/' + user + '/simplechaindb/clusterdeploy/rethinkdb-tests/rethindbTest02.py' #single 1.4M
       py_path3 = '/home/' + user + '/simplechaindb/clusterdeploy/rethinkdb-tests/rethindbTest03.py' #single 2.8M
       if file == '1':
           cmd = 'python3 {} {} {}'.format( py_path1,num,blank)
           sudo('echo execu {}'.format(cmd))
           sudo(cmd)
       elif file == '2':
           cmd = 'python3 {} {}'.format(py_path2,blank)
           sudo('echo execu {}'.format(cmd))
           sudo(cmd)
       elif file == '3':
           cmd = 'python3 {} {}'.format(py_path3,blank)
           sudo('echo execu {}'.format(cmd))
           sudo(cmd)
       sudo('echo test_node_rethinkdb')


# clean the old install & data
@task
@parallel
def destroy_all_nodes():
    with settings(warn_only=True):
        sudo('killall -9 bigchaindb')
        sudo('killall -9 simplechaindb')
        sudo('killall -9 unichain')
        sudo('killall -9 rethinkdb')

        sudo('rm -rf /data/rethinkdb/*')
        sudo('rm -rf /data/localdb/*')

        sudo('rm -rf /usr/local/lib/python3.4/dist-packages/BigchainDB-*')
        sudo('rm /usr/local/bin/bigchaindb')
        sudo('rm -rf ~/bigchaindb')
        sudo('rm /usr/local/bin/simplechaindb')
        sudo('rm -rf ~/simplechaindb')
        sudo('rm /usr/local/bin/unichain')
        sudo('rm -rf ~/unichain')
        # sudo('apt-get purge rabbitmq-server')

################################ Detect server ######################################
#step: get port & detect port & detect process
@task
def detect_rethinkdb():
    with settings(warn_only=True):
        #TODO:
        pass

#step: get port & detect port & detect process
@task
def detect_localdb():
    with settings(warn_only=True):
        #TODO:
        pass

#step: get port & detect port & detect process
@task
def detect_unichain_pro():
    with settings(warn_only=True):
        #TODO:
        pass

#step: get port & detect port & detect process
@task
def detect_unichain_api():
    with settings(warn_only=True):
        #TODO:
        pass
