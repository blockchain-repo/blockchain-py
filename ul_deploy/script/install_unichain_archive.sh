#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

CUR_INSTALL_PATH=$(cd "$(dirname "$0")"; pwd)
rm -f ${CUR_INSTALL_PATH}/unichain_cash-archive.tar.gz 2>/dev/null

[ $# -lt 1 ] && echo -e "[ERROR]install_unichain_cash_archive.sh need param!!!" && exit 1

install_orig=$1
install_tag=$2
if [ $install_orig == "git" ];then
    [ $# -lt 2 ] && echo -e "[ERROR]install_unichain_cash_archive.sh need 2 param!!!" && exit 1
    cd ../../
    git archive ${install_tag} --format=tar --output=unichain_cash-archive.tar
    gzip unichain_cash-archive.tar
    mv unichain_cash-archive.tar.gz ul_deploy/script/
    cd -
elif [ $install_orig == "local" ];then
    cd ../../
    tar -cf unichain_cash-archive.tar *
    gzip unichain_cash-archive.tar
    mv unichain_cash-archive.tar.gz ul_deploy/script/
    cd -
fi

fab install_unichain_from_git_archive

rm -f ${CUR_INSTALL_PATH}/unichain_cash-archive.tar.gz 2>/dev/null
