#!/bin/bash

__script_dir__=$(cd $(dirname ${0}) && pwd -P)
echo ${__script_dir__}
cd ${__script_dir__}
[[ -d __tmp__ ]] && rm -rf __tmp__
mkdir -p ${__script_dir__}/__tmp__
cd __tmp__

# install automake 1.15
tar xzf ${__script_dir__}/automake-1.15.tar.gz
(cd automake-1.15; ./configure --prefix=$HOME/usr; make && make install)

# install global
tar xzf ${__script_dir__}/global-6.5.tar.gz
(cd global-6.5; ./configure --prefix=$HOME/usr; make && make install)
