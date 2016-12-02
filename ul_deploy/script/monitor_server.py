# -*- coding: utf-8 -*-\n

import os.path

gMonitorServer = None
monitor_conf_filename = "monitor_config"

# cwd = current working directory
old_cwd = os.getcwd()

os.chdir('../conf')
conf_path = os.getcwd()
monitor_conf_file_path = conf_path + '/' + monitor_conf_filename

with open(monitor_conf_file_path) as f:
    for line in f.readlines():
        line = line.strip()
        if not len(line) or line.startswith('#'):
            continue
        if line.find("=") < 0:
            exit("Error gMonitorServers info in {}".format(monitor_conf_file_path))

        gMonitorServers = line.split("=")
        gMonitorServer =  gMonitorServers[1].strip()
        # print(gMonitorServer)
    conf_path = os.getcwd()