#!/bin/bash

setup_dir="$HOME/.BCloud"
bin_dir="$setup_dir/bin"
lib_dir="$setup_dir/bin/python/lib"
python_dir="$setup_dir/bin/python"
python_fileRH="Python.tar.gz"
python_file6u3="Python6u3.tar.gz"
python_file4u3="Python4u3.tar.gz"
bcloud_file="bcloud.tar.gz"
url="http://buildkit.scm.baidu.com/bcloud/package"
bcloud_url="$url/$bcloud_file"
bcloud_proxy_url="$url/bcloud"
source_path="NO"
add_lib_path="NO"
os_version_file="/etc/redhat-release"
redhat_version="Red Hat Enterprise Linux AS release 4 (Nahant Update 3)"
centos_4u3_version="CentOS release 4.3 (Final)"
centos_6u3_version="CentOS release 6.3 (Final)"

modify_path()
{
    grep -v "^#" $HOME/.bash_profile | grep "PATH=$1:\$PATH" >/dev/null 2>&1
    local ret0=$?
    grep -v "^#" $HOME/.bashrc | grep "PATH=$1:\$PATH" >/dev/null 2>&1
    local ret1=$?
    local ret=$[$ret0*$ret1]
    if [ $ret -ne 0 ];then
        echo "PATH=$1:\$PATH" >> $HOME/.bash_profile
        echo "export PATH" >> $HOME/.bash_profile
        source_path="YES"
    fi
}

modify_ld_library_path()
{
    grep -v "^#" $HOME/.bash_profile | grep "LD_LIBRARY_PATH=$1:\$LD_LIBRARY_PATH" >/dev/null 2>&1
    local ret0=$?
    grep -v "^#" $HOME/.bashrc | grep "LD_LIBRARY_PATH=$1:\$LD_LIBRARY_PATH" >/dev/null 2>&1
    local ret1=$?
    local ret=$[$ret0*$ret1]
    if [ $ret -ne 0 ];then
        echo "LD_LIBRARY_PATH=$1:\$LD_LIBRARY_PATH" >> $HOME/.bash_profile
        echo "export LD_LIBRARY_PATH" >> $HOME/.bash_profile
        source_path="YES"
    fi
}

if [ ! -e $setup_dir ]; then
    mkdir -p $setup_dir
    if [ $? -ne 0 ]; then
        echo "'mkdir -p $setup_dir' for BCloud error!"
        exit 1
    fi
fi

if [ ! -e $bin_dir ]; then
    mkdir -p $bin_dir
    if [ $? -ne 0 ]; then
        echo "'mkdir -p $bin_dir' for BCloud error!"
        exit 1
    fi
fi

if [ ! -e $python_dir ]; then
    mkdir -p $python_dir
    if [ $? -ne 0 ]; then
        echo "'mkdir -p $python_dir' for BCloud error!"
        exit 1
    fi
fi

#删除之前bcloud安装的svn 1.7
bcloud_svn="$bin_dir/svn"
if [ -e $bcloud_svn ]; then
    rm $bcloud_svn
fi

#检查python版本号
#如果<=2.7下载新版
#这里总是下载BCLOUD自己的python，以避免和用户环境的python冲突
need_update_py='YES'
#need_update_py='NO'
#has_python=`which python`
#if [ $? -ne 0 ]; then
#    need_update_py='YES'
#else
#    local_py_ver=`python -V 2>&1`
#    #echo $local_py_ver
#    local_py_ver=`echo $local_py_ver | awk '{print $2}'`
#    local_py_ver1=`echo $local_py_ver | awk -F '.' '{print $1}'`
#    local_py_ver2=`echo $local_py_ver | awk -F '.' '{print $2}'`
#    local_py_ver3=`echo $local_py_ver | awk -F '.' '{print $3}'`
#
#    if [ $local_py_ver1 -lt 2 ]; then
#        need_update_py='YES'
#    elif [ $local_py_ver1 -eq 2 ] && [ $local_py_ver2 -lt 7 ]; then
#        need_update_py='YES'
#    elif [ $local_py_ver1 -gt 2 ]; then
#        need_update_py='YES'
#    fi
#fi
if [ ! -e $os_version_file ]; then
    echo "can not check OS version"
    exit 1
fi

OS_VER=`cat $os_version_file`
if [ "$OS_VER" == "$redhat_version" ]; then
    python_file=$python_fileRH
fi 

if [ "$OS_VER" == "$centos_4u3_version" ]; then
    python_file=$python_file4u3
fi 

if [ "$OS_VER" == "$centos_6u3_version" ]; then
    python_file=$python_file6u3
fi 

python_file=$python_file6u3
python_url="$url/$python_file"

if [ "$need_update_py" == 'YES' ]; then
    echo "setup python ..."
    cd $python_dir
    if [ -e $python_file ]; then
        rm $python_file
    fi
    wget $python_url .
    if [ ! -e $python_file ]; then
        echo "get python from remote error!"
	exit 2
    fi

    tar zxf $python_file
    if [ $? -ne 0 ]; then
        echo "setup python error!"
	exit 3
    fi

    echo "setup python success."
    rm $python_file
    cd -
fi

#下载bcloud
cd $setup_dir
echo "setup bcloud ..."
if [ -e $bcloud_file ]; then
    rm $bcloud_file
fi

wget $bcloud_url .
if [ ! -e $bcloud_file ]; then
    echo "get bcloud from remote error!"
    exit 2
fi

tar zxf $bcloud_file
if [ $? -ne 0 ]; then
    echo "setup bcloud error!"
    exit 3
fi

cd $bin_dir
bcloud="bcloud"
if [ -e $bcloud ] || [ -L $bcloud ]; then
    rm $bcloud
fi
#下载bcloud代理文件
wget $bcloud_proxy_url .
chmod +x ./bcloud
cd -

echo "setup bcloud success."
rm $bcloud_file


#加入环境变量
modify_path $bin_dir
if [ "$add_lib_path" == "YES" ]; then
    modify_ld_library_path $lib_dir
fi
if [ "$source_path" == "YES" ]; then
    echo -e "\033[;31mPlease run \033[;32msource ~/.bash_profile\033[0m"
fi
