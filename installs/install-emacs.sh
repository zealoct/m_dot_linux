#!/bin/bash

__script_dir__=$(cd $(dirname ${0}) && pwd -P)

sudo yum -y groupinstall "Development Tools"
sudo yum -y install gtk+-devel gtk2-devel
sudo yum -y install libXpm-devel
sudo yum -y install libpng-devel
sudo yum -y install giflib-devel
sudo yum -y install libtiff-devel libjpeg-devel
sudo yum -y install ncurses-devel
sudo yum -y install gpm-devel dbus-devel dbus-glib-devel dbus-python
sudo yum -y install GConf2-devel pkgconfigy
sudo yum -y install libXft-devel

echo ${__script_dir__}
cd ${__script_dir__}
[[ -d __tmp__ ]] && rm -rf __tmp__
mkdir -p ${__script_dir__}/__tmp__
cd __tmp__

export PATH=$HOME/usr/bin:$HOME/usr/bin/gcc:/sbin:/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:/opt/bin

tar xzf ${__script_dir__}/emacs-26.1.tar.gz
(cd emacs-emacs-26.1 && ./autogen.sh && ./configure --prefix=$HOME/usr && make && make install)
