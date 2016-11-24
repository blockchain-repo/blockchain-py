#!/bin/bash

set -e

source ./check_tools_util.sh

echo -e "[INOF]==========init env: begin=========="
python_bin=`check_python_3`
[ -z "$python_bin" ] && {
    echo -e "[WARNING]==========python3 not exist,install begin=========="
    #install python3
    sudo add-apt-repository ppa:fkrull/deadsnakes
    sudo apt-get update
    sudo apt-get install python3.5

    #set Python3.5 defalt cmd
    rm /usr/local/bin/python >/dev/null
    ln -s /usr/local/bin/python3.5 /usr/local/bin/python 

    #uninstall python3
    #sudo apt-get remove python3.5
    echo -e "[WARNING]==========python3 install end=========="
} || {
    echo -e "[WARNING]==========python3 set default begin=========="
    python_bin_path=`get_python_bin_path ${python_bin}`
    [[ ! -z $python_bin_path ]] && {
        sudo rm /usr/local/bin/python 2>/dev/null
        sudo ln -s $python_bin_path /usr/local/bin/python
    }
    echo -e "[WARNING]==========python3 set default end=========="
}

fab_version=`check_fabric_3`
[ -z "$fab_version" ] && {
    echo -e "[WARNING]==========fab3 not exist,install begin=========="
    sudo pip3 install fabric3
    echo -e "[WARNING]==========fab3 install end=========="
}
echo -e "[INOF]==========init env: done=========="

exit 0
