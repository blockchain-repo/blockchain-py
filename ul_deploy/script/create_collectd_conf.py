# -*- coding: utf-8 -*-
"""(Re)create the collectd configuration file conf/collectd.conf
Start with conf/collectd.conf.template
then append additional configuration setting, ie. monitor server.
"""

from __future__ import unicode_literals
import os
import shutil

from monitor_server import gMonitorServer


conf_filename = "collectd.conf"
conf_template_filename = conf_filename + ".template"
monitor_conf_filename = "monitor_config"

# cwd = current working directory
old_cwd = os.getcwd()

os.chdir('../conf')
conf_path = os.getcwd()
conf_file_path = conf_path + '/' + conf_filename
monitor_conf_file_path = conf_path + '/' + monitor_conf_filename

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

# Create the initial collectd.conf using collectd.conf.template
shutil.copy2(conf_template_filename, conf_file_path)
print("Create file {} success!".format(conf_filename))


# Append additional lines to collectd.conf
with open(conf_file_path, 'a') as f:
    f.write('''
<Plugin network>
    Server "''' + gMonitorServer + '''" "25826"
</Plugin>
    ''')

print('gMonitorServer {}'.format(gMonitorServer))
print('Create the conf file {} success!'.format(monitor_conf_file_path))