#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

cd ..
rm -f unichain-archive.tar.gz

cd ..
git archive master --format=tar --output=unichain-archive.tar
gzip unichain-archive.tar

mv unichain-archive.tar.gz ul-deploy/

cd ul-deploy/script
fab install_unichain_from_git_archive

cd ..
rm unichain-archive.tar.gz

