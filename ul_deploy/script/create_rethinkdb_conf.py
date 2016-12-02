# -*- coding: utf-8 -*-
"""(Re)create the RethinkDB configuration file conf/rethinkdb.conf.
Start with conf/rethinkdb.conf.template
then append additional configuration settings (lines).
"""

from __future__ import unicode_literals
import os.path
import shutil

from hostlist import public_hosts


conf_filename = "rethinkdb.conf"
conf_template_filename = conf_filename + ".template"

# cwd = current working directory
old_cwd = os.getcwd()

os.chdir('../conf')
conf_path = os.getcwd()
conf_file_path = conf_path + '/' + conf_filename
os.chdir('template')
conf_template_path = os.getcwd()

#template file exist
existTemplateFile = os.path.isfile(conf_template_filename)
if not existTemplateFile:
    info = 'You lose the file {} in "{}"'.format(conf_template_filename,conf_template_path)
    os.chdir(old_cwd)
    exit(info)

#config file exist
if os.path.isfile(conf_filename):
    os.remove(conf_filename)
    print("Remove old file {}".format(conf_filename))


# Create the initial rethinkdb.conf using rethinkdb.conf.template
shutil.copy2(conf_template_filename, conf_file_path)
print("Create file {} success!".format(conf_filename))

# Append additional lines to rethinkdb.conf
with open(conf_file_path, 'a') as f:
    f.write('## The host:port of a node that RethinkDB will connect to\n')
    if public_hosts is not None and len(public_hosts) > 1 :
        for public_host in public_hosts:
            f.write('join=' + public_host + ':29015\n')

os.chdir(old_cwd)

