
# -*- coding: utf-8 -*-

"""A Fabric fabfile with functionality to prepare, install, and configure
BigchainDB, including its storage backend (RethinkDB).
"""

from __future__ import with_statement, unicode_literals

from os import environ  # a mapping (like a dict)
import sys

from fabric.api import sudo,cd, env, hosts
from fabric.api import task, parallel
from fabric.contrib.files import sed
from fabric.operations import run, put, get
from fabric.context_managers import settings

import json
from hostlist import public_dns_names,public_hosts,public_pwds,public_host_pwds

################################ Fabric Initial Config Data  ######################################

env['passwords'] = public_host_pwds
env['hosts']=env['passwords'].keys()

################################ Check envl  ######################################
#step:check port&process&data,conf path
@task
def check_rethinkdb():
    with settings(warn_only=True):
        print("[INFO]==========check rethinkdb begin==========")
        process_num=run('ps -aux|grep -E "/usr/bin/rethinkdb"|grep -v grep|wc -l')
        if process_num == 0:
            print("[INFO]=====process[rethinkdb] num detect result: is 0")
        else:
            print("[ERROR]=====process[rethinkdb] num detect result: is %s" % (str(process_num)))
        #TODO:read from conf
        driver_port = 28015
        cluster_port = 29015
        http_port = 8080
        check_driver_port=sudo('netstat -nlap|grep "LISTEN"|grep rethinkdb|grep ":%s"' % (driver_port))
        if not check_driver_port:
            print("[INFO]=====driver_port[%s] detect result: is not used!" % (driver_port))
        else:
            print("[ERROR]=====driver_port[%s] detect result: is used!" % (driver_port))
        check_cluster_port=sudo('netstat -nlap|grep "LISTEN"|grep rethinkdb|grep ":%s"' % (cluster_port))
        if not check_cluster_port:
            print("[INFO]=====cluster_port[%s] detect result: is not used!" % (cluster_port))
        else:
            print("[ERROR]=====cluster_port[%s] detect result:  is used!" % (cluster_port))
        check_http_port=sudo('netstat -nlap|grep "LISTEN"|grep rethinkdb|grep ":%s"' % (http_port))
        if not check_http_port:
            print("[INFO]=====http_port[%s] detect result: is not used!" % (http_port))
        else:
            print("[ERROR]=====http_port[%s] detect result: is used!" % (http_port))

#step:check port&process&data,conf path
@task
def check_localdb():
    with settings(warn_only=True):
        #TODO:
        pass

#step:check port&process&data,conf path
@task
def check_unichain():
    with settings(warn_only=True):
        print("[INFO]==========check unichain pro begin==========")
        process_num=run('ps -aux|grep -E "/usr/local/bin/unichain -y start|SCREEN -d -m unichain -y start"|grep -v grep|wc -l')
        if process_num == 0:
            print("[INFO]=====process[unichain] num check result: is 0")
        else:
            print("[ERROR]=====process[unichain] num check result: is %s" % (str(process_num)))
        ##TODO:confirm port in conf
        api_port=9984
        check_api_port=sudo('netstat -nlap|grep "LISTEN"|awk -v v_port=":%s" \'{if(v_port==$4) print $0}\'' % (api_port))
        if not check_api_port:
            print("[INFO]=====api_port[%s] detect result: is not used!" % (api_port))
        else:
            print("[ERROR]=====api_port[%s] detect result: is used!" % (api_port))

#step:check port&process&data,conf path
@task
def check_unichain_api():
    with settings(warn_only=True):
        print("[INFO]==========check unichain api begin==========")
        process_num=run('ps -aux|grep -E "/usr/local/bin/unichain_api start|SCREEN -d -m unichain_api start"|grep -v grep|wc -l')
        if process_num == 0:
            print("[INFO]=====process[unichain_api] num check result: is 0")
        else:
            print("[ERROR]=====process[unichain_api] num check result: is %s" % (str(process_num)))
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
        will set env.hosts = [public_dns_names[4]]
        but only for doing fab_task_A and fab_task_B
    """
    env.hosts = [public_dns_names[int(host_index)]]
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
        #update by  mayx, op at start_all
        # finally restart instance
        #sudo('service collectd restart', pty=False)


@task
@parallel
def start_collectd():
    """Installation of Collectd"""
    with settings(warn_only=True):
        sudo("echo 'collectd restart' ")
        sudo('service collectd restart', pty=False)


@task
@parallel
def stop_collectd():
    """Installation of Collectd"""
    with settings(warn_only=True):
        sudo("echo 'collectd stop' ")
        sudo('service collectd stop', pty=False)


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
        #update by  mayx, op at start_all
        # finally restart instance  
        #sudo('/etc/init.d/rethinkdb restart')


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
    put('unichain-archive.tar.gz')
    user_group = env.user
    with settings(warn_only=True):
        if run("test -d ./unichain").failed:
            run("echo 'create unichain directory' ")
            sudo("mkdir -p ./unichain",user=env.user,group=env.user)
            #sudo("chown -R " + user_group + ':' + user_group + ' ~/')
        else:
            run("echo 'remove old unichain directory' ")
            sudo("rm -rf ./unichain/*")
    run('tar xvfz unichain-archive.tar.gz -C ./unichain >/dev/null 2>&1')
    sudo('pip3 install -i http://pypi.douban.com/simple --upgrade setuptools')
    with cd('./unichain'):
        sudo('python3 setup.py install')
        # sudo('pip3 install .')
    sudo('rm -f ../unichain-archive.tar.gz')
    run('echo install_unichain_from_git_archive done!')


# install localdb
@task
@parallel
def install_localdb():
    # leveldb & plyvel install
    with settings(warn_only=True):
        user_group = env.user
        sudo("echo 'leveldb & plyvel install' ")
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
        sudo("mkdir -p /data/localdb/{node_info,block,block_header,block_records,vote,vote_header}")
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
        run('echo "[INFO]==========uninstall unichain-pro=========="')
        sudo('killall -9 unichain 2>/dev/null')
        sudo('killall -9 unichain_api 2>/dev/null')
        sudo('killall -9 pip,pip3 2>/dev/null')
        sudo('rm /usr/local/bin/unichain 2>/dev/null')
        sudo('rm -rf /usr/local/lib/python3.4/dist-packages/BigchainDB-* 2>/dev/null')
        sudo('rm -rf ~/unichain 2>/dev/null')


# Initialize BigchainDB
# i.e. create the database, the tables,
# the indexes, and the genesis block.
# (The @hosts decorator is used to make this
# task run on only one node. See http://tinyurl.com/h9qqf3t )
@task
@hosts(public_dns_names[0])
def init_unichain():
    with settings(warn_only=True):
        run('unichain -y drop',pty=False)
        run('unichain init', pty=False)
        set_shards()
        set_replicas()


# Configure BigchainDB
@task
@parallel
def configure_unichain():
    run('unichain -y configure', pty=False)


@task
@hosts(public_dns_names[0])
def drop_unichain():
    with settings(warn_only=True):
        run('unichain -y drop', pty=False)


# Set the number of shards (tables[bigchain,votes,backlog])
@task
@hosts(public_dns_names[0])
def set_shards(num_shards=len(public_dns_names)):
    # num_shards = len(public_hosts)
    run('unichain set-shards {}'.format(num_shards))
    run("echo set shards = {}".format(num_shards))


# Set the number of replicas (tables[bigchain,votes,backlog])
@task
@hosts(public_dns_names[0])
def set_replicas(num_replicas=(int(len(public_dns_names)/2)+1)):
    run('unichain set-replicas {}'.format(num_replicas))
    run("echo set replicas = {}".format(num_replicas))

# unichain_restore_app
@task
@parallel
def start_unichain_restore():
    with settings(warn_only=True):
        sudo('screen -d -m unichain_restore -y start &', pty=False, user=env.user)

@task
@parallel
def stop_unichain_restore(port=9986):
    with settings(warn_only=True):
        sudo("killall -9 unichain_restore 2>/dev/null")
        try:
            sudo("kill -9 `netstat -nlp | grep :{} | awk '{print $7}' | awk -F'/' '{ print $1 }'`".format(port))
        except:
            pass
        run("echo stop unichain_restore and kill the port {}".format(port))

# unichain
@task
@parallel
def start_unichain():
    with settings(warn_only=True):
        stop_unichain_restore()
        sudo('screen -d -m unichain -y start &', pty=False, user=env.user)
        sudo('screen -d -m unichain_api start &', pty=False, user=env.user)


@task
@parallel
def stop_unichain():
    with settings(warn_only=True):
        # sudo("kill `ps -ef|grep unichain | grep -v grep|awk '{print $2}'` ")
        sudo("killall -9 unichain_api 2>/dev/null")
        sudo("killall -9 unichain 2>/dev/null")


@task
@parallel
def restart_unichain():
    with settings(warn_only=True):
        sudo("killall -9 unichain_api 2>/dev/null")
        sudo("killall -9 unichain 2>/dev/null")
        sudo('screen -d -m unichain -y start &', pty=False, user=env.user)
        sudo('screen -d -m unichain_api start &', pty=False, user=env.user)


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
        run("echo clean rethinkdb data")
        sudo('rm -rf /data/rethinkdb/* 2>/dev/null')


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


# python3,pip,pip3
@task 
def stop_python():
    sudo("killall -9 python,python3,pip,pip3 2>/dev/null")

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
    """Security harden sshd."""

    # Enable password authentication
    sed('/etc/ssh/sshd_config',
        '#PasswordAuthentication yes',
        'PasswordAuthentication yes',
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
        sudo('killall -9 unichain 2>/dev/null')
        sudo('killall -9 unichain_api 2>/dev/null')
        sudo('killall -9 rethinkdb 2>/dev/null')
        sudo('killall -9 pip3,pip 2>/dev/null')
        sudo('rm /usr/local/bin/unichain 2>/dev/null')
        sudo('rm -rf /usr/local/lib/python3.4/dist-packages/BigchainDB-* 2>/dev/null')
        sudo('rm -rf ~/unichain 2>/dev/null')
        sudo('rm -rf /data/rethinkdb/* 2>/dev/null')
        sudo('rm -rf /data/localdb/{node_info,block,block_header,block_records,vote,vote_header}/* 2>/dev/null')


@task
@parallel
def kill_all_nodes():
    with settings(warn_only=True):
        sudo('killall -9 unichain 2>/dev/null')
        sudo('killall -9 unichain_api 2>/dev/null')
        sudo('killall -9 rethinkdb 2>/dev/null')
        sudo('killall -9 pip3,pip 2>/dev/null')


@task
@parallel
def kill_process_with_name(name):
    with settings(warn_only=True):
        if name is not None:
            run("echo kill process use the name %s" %(name))
            sudo("killall -9 {}".format(name))


@task
@parallel
def kill_process_with_port(port):
    with settings(warn_only=True):
        run("echo kill process use the port %s" %(port))
        try:
            sudo("kill -9 `netstat -nlp | grep :{} | awk '{print $7}' | awk -F'/' '{ print $1 }'`".format(port))
        except:
            pass

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
def append_rethinkdb_join(port=29015):
    with settings(warn_only=True):
        if port is None:
            port = 29015
        join_infos =""
        rethinkdb_conf_path = "/etc/rethinkdb/instances.d/default.conf"
        for host in public_hosts:
            join_info = "join={}:{}".format(host,port)
            join_infos += join_info + "\\n"
            sudo("echo {} {}".format(host,join_info))
        join_infos =join_infos[:-2]
        sudo("echo 'The joins will write to {}:\n{}'".format(rethinkdb_conf_path,join_infos))
        if join_infos != '':
           sudo("sed -i '$a {}' /etc/rethinkdb/instances.d/default.conf".format(join_infos))


@task
@parallel
def rewrite_rethinkdb_join(port=29015):
    with settings(warn_only=True):
        if port is None:
            port = 29015
        join_infos =""
        rethinkdb_conf_path = "/etc/rethinkdb/instances.d/default.conf"
        for host in public_hosts:
            join_info = "join={}:{}".format(host,port)
            join_infos += join_info + "\\n"
            sudo("echo {} {}".format(host,join_info))
        join_infos =join_infos[:-2]
        sudo("echo 'The joins will write to {}:\n{}'".format(rethinkdb_conf_path,join_infos))
        if join_infos != '':
           sudo("sed -i '/^\s*join=/d' /etc/rethinkdb/instances.d/default.conf")
           sudo("sed -i '$a {}' /etc/rethinkdb/instances.d/default.conf".format(join_infos))


@task
@parallel
def remove_rethinkdb_join():
    with settings(warn_only=True):
         sudo("sed -i '/^\s*join=/d' /etc/rethinkdb/instances.d/default.conf")


@task
@parallel
def seek_rethinkdb_join():
    with settings(warn_only=True):
         sudo("sed -n '/^\s*join=/p' /etc/rethinkdb/instances.d/default.conf")


@task
@parallel
def start_unichain_load_processes_counts(m=1,c=None):
    sudo("echo " + 'm={} c={} &'.format(m, c))
    if m is None and c is None:
        sudo('screen -d -m unichain load &', pty=False,user=env.user)
    flag = ''
    v = None
    if m :
        flag=flag+'m'
        v = m
    if c :
        flag=flag+'c'
        v = c
    if len(flag) == 1:
        cmd = 'screen -d -m unichain load -{} {} &'.format(flag, v)
        sudo(cmd, pty=False,user=env.user)
        sudo("echo {}".format(cmd) )

    if len(flag) == 2:
        cmd = 'screen -d -m unichain load -m {} -c {} &'.format(m, c)
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
        sudo('killall -9 bigchaindb 2>/dev/null')
        sudo('killall -9 simplechaindb 2>/dev/null')
        sudo('killall -9 unichain 2>/dev/null')
        sudo('killall -9 unichain_api 2>/dev/null')
        sudo('killall -9 rethinkdb 2>/dev/null')
        sudo('killall -9 pip,pip3 2>/dev/null')

        sudo('rm -rf /data/rethinkdb/* 2>/dev/null')
        sudo('rm -rf /data/localdb/{node_info,block,block_header,block_records,vote,vote_header}/* 2>/dev/null')

        sudo('rm -rf /usr/local/lib/python3.4/dist-packages/BigchainDB-* 2>/dev/null')
        sudo('rm /usr/local/bin/bigchaindb 2>/dev/null')
        sudo('rm -rf ~/bigchaindb 2>/dev/null')
        sudo('rm /usr/local/bin/simplechaindb 2>/dev/null')
        sudo('rm -rf ~/simplechaindb 2>/dev/null')
        sudo('rm /usr/local/bin/unichain 2>/dev/null')
        sudo('rm -rf ~/unichain 2>/dev/null')
        # sudo('apt-get purge rabbitmq-server')

################################ Detect server ######################################
#step: get port & detect port
@task
def detect_rethinkdb():
    with settings(warn_only=True):
        print("[INFO]==========detect rethinkdb begin==========")
        rethinkdb_conf = "/etc/rethinkdb/instances.d/default.conf"
        driver_port = sudo('cat %s|grep -v "^#"|grep "driver-port="|awk -F"=" \'{print $2}\'' % (rethinkdb_conf))
        cluster_port = sudo('cat %s|grep -v "^#"|grep "cluster-port="|awk -F"=" \'{print $2}\'' % (rethinkdb_conf))
        http_port = sudo('cat %s|grep -v "^#"|grep "http-port="|awk -F"=" \'{print $2}\'' % (rethinkdb_conf))
        if not driver_port :
            driver_port = 28015 
        if not cluster_port:
            cluster_port = 29015 
        if not http_port:
            http_port = 8080
        check_driver_port=sudo('netstat -nlap|grep "LISTEN"|grep rethinkdb|grep ":%s"' % (driver_port))
        if not check_driver_port:
            print("[ERROR]=====driver_port[%s] detect result: NOT exist!" % (driver_port))
        else:
            print("[INFO]=====driver_port[%s] detect result: is OK!" % (driver_port))
        check_cluster_port=sudo('netstat -nlap|grep "LISTEN"|grep rethinkdb|grep ":%s"' % (cluster_port))
        if not check_cluster_port:
            print("[ERROR]=====cluster_port[%s] detect result: not alive" % (cluster_port))
        else:
            print("[INFO]=====cluster_port[%s] detect result:  is OK!" % (cluster_port))
        check_http_port=sudo('netstat -nlap|grep "LISTEN"|grep rethinkdb|grep ":%s"' % (http_port))
        if not check_http_port:
            print("[ERROR]=====http_port[%s] detect result: not alive" % (http_port))
        else:
            print("[INFO]=====http_port[%s] detect result: is OK!" % (http_port))
        process_num=run('ps -aux|grep -E "/usr/bin/rethinkdb"|grep -v grep|wc -l')
        if process_num == 0:
            print("[ERROR]=====process[rethinkdb] num detect result: is 0")
        else:
            print("[INFO]=====process[rethinkdb] num detect result: is %s" % (str(process_num)))


#step: get port & detect port & detect process
@task
def detect_localdb():
    with settings(warn_only=True):
        #TODO:
        pass

#step: get port & detect port & detect process
@task
def detect_unichain():
    with settings(warn_only=True):
        print("[INFO]==========detect unichain pro begin==========")
        process_num=run('ps -aux|grep -E "/usr/local/bin/unichain -y start|SCREEN -d -m unichain -y start"|grep -v grep|wc -l')
        if int(process_num) == 0:
            print("[ERROR]=====process[unichain] num detect result: is 0")
        else:
            print("[INFO]=====process[unichain] num detect result: is %s" % (str(process_num)))

#step: get port & detect port & detect process
@task
def detect_unichain_api():
    with settings(warn_only=True):
        print("[INFO]==========detect unichain api begin==========")
        process_num=run('ps -aux|grep -E "/usr/local/bin/unichain_api start|SCREEN -d -m unichain_api start"|grep -v grep|wc -l')
        if int(process_num) == 0:
            print("[ERROR]=====process[unichain_api] num detect result: is 0")
        else:
            print("[INFO]=====process[unichain_api] num detect result: is %s" % (str(process_num)))

        unichain_conf = "/home/%s/.unichain" % (env.user)
        unichain_conf_str=run('cat ~/.unichain')
        #with open(unichain_conf, "a") as r:
        #    unichain_conf_str=r.readline()
        unichain_conf_str.replace("null", "")
        unichain_dict = json.loads(unichain_conf_str)
        server_url = str(unichain_dict["server"]["bind"])
        api_endpoint = str(unichain_dict["api_endpoint"])
        if server_url.startswith("0.0.0.0"):
            api_url = api_endpoint.replace("/api/v1", "")
            api_detect_res = run('curl -i %s 2>/dev/null|head -1|grep "200 OK"' % (api_url))
            if not api_detect_res:
                print("[ERROR]=====api[%s] detect result: is not requested!!!" % (api_url))
            else:
                print("[INFO]=====api[%s] detect result: is OK!" % (api_url))
        else:
            print("[ERROR]=====api[%s] detect result:  is not requested!" % (api_endpoint))

@task
@parallel
def clear_unichain_data(flag='rethinkdb'):
    with settings(warn_only=True):
        if flag == 'all':
            sudo('rm -rf /data/rethinkdb/*')
            sudo('rm -rf /data/localdb/*')
        elif flag == 'localdb':
            sudo('rm -rf /data/localdb/{node_info,block,block_header,block_records,vote,vote_header}/*')
        elif flag == 'rethinkdb':
            sudo('rm -rf /data/rethinkdb/*')
        if flag in ('all','localdb','rethinkdb'):
            info = "{} has clear the data in {}".format(env.user,flag if flag != 'all' else 'rethinkdb and localdb')
            sudo("echo {}".format(info))

@task
@parallel
def test_localdb_rethinkdb(args="-irbvt",filename="validate_localdb_format.py",datetimeformat="%Y%m%d%H"):
    with settings(warn_only=True):
        user = env.user
        with cd("~/unichain/ul_tests/localdb"):
            filename_prefix = filename.split(".")[0]
            if run("test -d test_result").failed:
                sudo("mkdir test_result", user=env.user, group=env.user)
            sudo("python3 {} {} | tee test_result/{}_{}_$(date +{}).txt".format(filename,args,user,filename_prefix,datetimeformat))
        sudo("echo 'test_localdb_rethinkdb over'")

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

################################ Docker related ######################################
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
