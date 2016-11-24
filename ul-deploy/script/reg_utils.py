# -*- coding: utf-8 -*-\n

import re

def reg_nodes(nodes=None):
    if nodes:
        pattern = re.compile(r"""^([^@]*) # hostname
                             @([^\s]*)    # ip
                             :(\d+)       # port
                             \s*([^\s]*)  # pwd
                             \s*\#*.*$    # comment
                             """, re.X)
        match = pattern.match(nodes)
        if  match:
            return match.groups()
        return False


def reg_ip(ip=None):
    if ip:
        pattern = re.compile(r"""^([1]?\d\d? | 2[0 - 4]\d | 25[0 - 5]) # part 1
                             \.([1]?\d\d? | 2[0 - 4]\d | 25[0 - 5])    # part 2
                             \.([1]?\d\d? | 2[0 - 4]\d | 25[0 - 5])    # part 3
                             \.([1]?\d\d? | 2[0 - 4]\d | 25[0 - 5])    # part 4
                             $""", re.X)
        match = pattern.match(ip)
        if not match:
            return False
        return True
