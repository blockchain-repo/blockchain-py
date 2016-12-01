#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e


CUR_INSTALL_PATH=$(cd "$(dirname "$0")"; pwd)
rm -f ${CUR_INSTALL_PATH}/unichain-archive.tar.gz

cd ../../
git archive dev --format=tar --output=unichain-archive.tar
gzip unichain-archive.tar
mv unichain-archive.tar.gz ul_deploy/script/
cd -

fab install_unichain_from_git_archive

rm -f ${CUR_INSTALL_PATH}/unichain-archive.tar.gz
