# -*- coding: utf-8 -*-\n

import os.path

# import reg_utils # usage reg_utils.reg_nodes,...

from reg_utils import reg_nodes,reg_ip

conf_filename = "blockchain_nodes"

# cwd = current working directory
old_cwd = os.getcwd()

os.chdir('../conf')
conf_path = os.getcwd()

blockchain_nodes_path = conf_path + "/"  + conf_filename
existNodesConfig = os.path.isfile(blockchain_nodes_path)

if not existNodesConfig:
    info = 'You lose the file {} in "{}"'.format(conf_filename,conf_path)
    os.chdir(old_cwd)
    exit(info)

# for fabric use
public_dns_names = []
public_pwds = []
public_host_pwds = {}

with open(blockchain_nodes_path) as f:
    for line in f.readlines():
        line = line.strip()
        if  not len(line) or line.startswith('#'):
            continue

        groups = reg_nodes(line)
        if groups:
            length = len(groups)
            if length < 4:
                exit('error format...')
            username = groups[0]
            host = groups[1]
            if not reg_ip(host):
                continue
            port = groups[2]
            pwd = groups[3]

            hosts = "{}@{}:{}".format(username, host, port)
            public_dns_names.append(hosts)
            public_pwds.append(pwd)
            public_host_pwds[hosts] = pwd

    os.chdir(old_cwd)