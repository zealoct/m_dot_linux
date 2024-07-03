#!/bin/bash
ERR=1
OK=0
_USERHOME=$HOME

Install_client()
{
    echo ${RSYNC_SERVER:="getprod.scm.baidu.com"} 2>&1 >&/dev/null
    RSYNC_LOG="$HOME/.rsync.log"
    PARM=" --progress --port=8990 -vuHrltpD --force"
    User="scmtools"
    export  RSYNC_PASSWORD="scm123"
        
    rsync $PARM $User@$RSYNC_SERVER::compile-optim/latest/linux/client/*  $SCMTOOLS_PATH/  2>>$RSYNC_LOG >> $RSYNC_LOG
        
    if [ $?  != 0 ];then
        echo "Errro: rsync scmtools files failed, please contact scm, hi group: 1354895"
        return $ERR
    fi      
        
    unset  RSYNC_PASSWORD
    install -m 775 -d $SCMTOOLS_PATH/var/ccache_dir
    install -m 775 -d $SCMTOOLS_PATH/tmp
    if [ $? != 0 ];then
        echo  "[Warning] Fail to initialize dirs for ccache" | tee -a $RSYNC_LOG
    fi

    chmod g+s $SCMTOOLS_PATH/_scmtools/ccache/bin/ccache1
    if [ $? != 0 ];then
        echo  "[Warning] Fail to setgid for ccache1" | tee -a $RSYNC_LOG
    fi
    chmod g+s $SCMTOOLS_PATH/_scmtools/mcache/mcache
    if [ $? != 0 ];then
        echo  "[Warning] Fail to setgid for mcache" | tee -a $RSYNC_LOG
    fi

    umask 002
    if [ `uname -o` != "Cygwin" ];then
        CCACHE_DIR=$SCMTOOLS_PATH/var/ccache_dir $SCMTOOLS_PATH/usr/bin/ccache -M 30G -F 0
    fi
    crontab -l | grep -v "$SCMTOOLS_PATH/usr/bin/scmtools -u"  >~/.cronjobs
	randomnum=`date +%N`
	randomnum2=`expr $randomnum / 1000`
	minute=`expr $randomnum2 % 60`
	echo "$minute 08 * * * sh $SCMTOOLS_PATH/usr/bin/scmtools -u" >>~/.cronjobs
    crontab ~/.cronjobs
    echo "****** Created cronjob for daily update of scmtools ******"
    rm -f ~/.cronjobs
    echo -e "****** Success to update scmtools to the latest version ******"
    sh $SCMTOOLS_PATH/usr/bin/scmtools.sh -v |tee $SCMTOOLS_PATH/usr/bin/.scmtools.version
    $SCMTOOLS_PATH/usr/bin/bcloud version
    return $OK
}

createConFile()
{
    mkdir -p $SCMTOOLS_PATH/_scmtools
    mkdir -p $SCMTOOLS_PATH/usr/bin
    echo ${RSYNC_SERVER:="getprod.scm.baidu.com"} 2>&1 >&/dev/null
    if [ -d "$SCMTOOLS_PATH/_scmtools" ];then
        echo "[Mail]
value=

#Don't modify following info please!
[InstallDir]
value=$SCMTOOLS_PATH

[ProductHost]
value=${RSYNC_SERVER}" > ${SCMTOOLS_PATH}/_scmtools/scmtools.conf
        cd ${SCMTOOLS_PATH}/usr/bin/
        ln -sf ../../_scmtools/scmtools.conf 2>&1 >&/dev/null
        cd -
        return $OK
    else
        echo "Can not find $SCMTOOLS_PATH/_scmtools/scmtools.sh"
        return $ERR
    fi
}

Usage ()
{
	echo "To install scmtools, just run: install.sh <directory>"
	exit 0
}

modify_path()
{
    grep -v "^#" $_USERHOME/.bash_profile | grep PATH | grep $1 >/dev/null 2>&1
    local ret0=$?
    grep -v "^#" $_USERHOME/.bashrc | grep PATH | grep $1 >/dev/null 2>&1
    local ret1=$?
    local ret=$[$ret0*$ret1]
    if [ $ret -ne 0 ];then
        echo "PATH=$1/usr/bin:\$PATH" >> $_USERHOME/.bash_profile
        echo "export PATH" >> $_USERHOME/.bash_profile
        echo -e "\033[;31mPlease run \033[;32msource ~/.bash_profile\033[0m"
    fi
}

clean_ubuntu_env()
{
local OSreal=$(cat /etc/issue)
local Compare="Ubuntu"
local Compare_CentOS6="CentOS release 6.3 (Final)"

    if [ "${OSreal/$Compare/}" != "$OSreal" -o "${OSreal/$Compare_CentOS6/}" != "$OSreal" ];then
        rm -f ${SCMTOOLS_PATH}/usr/bin/python*
    fi
    return $OK
}

Main ()
{
    if [ $(readlink /bin/sh) == "dash" ];then
        echo "Please run below command at first:"
        echo -e "\033[;31m sudo dpkg-reconfigure dash\033[0m"
        echo -e "\033[;32m And then choose \"No\" \033[0m"
        exit 1
    fi

        if [[ $# -lt 1 || $# -eq 2 || $# -gt 3 ]];then
            echo "Invalid argument. Please use command: install.sh <directory>"
            exit 1
        elif [[ $# -eq 3 && "$2" != "-s" ]]; then
            echo "Invalid argument. Please use command: install.sh <directory>"
            exit 1
        elif [[ $# -eq 3 && ! $(echo "$3" | grep ".baidu.com$") ]];then
            echo "Invalid argument. the format of product hostname is wrong!" 
            exit 1
        fi
        if [ -f $1 -o -d $1 ]; then
            echo "Path $1 exists. Do you want to cleanup it? (y/n)"
            read yes
            if [ $yes == "y" ]; then
                suffix=$(echo $1| sed -n s'/.*\(.$\)/\1/p')
                if [ "$suffix" = "/" ];then
                    inst=$(echo $1| sed -n s'/.$//p')
                    rm -rf $inst
                else
                    rm -rf $1
                fi
            fi
        fi

        for opt in $@
        do
        case $opt in
                -h|--help)
                    Usage
                    ;;
                -s)
                    RSYNC_SERVER=$3
                    ;;
        esac
        done

	echo "mkdir $1 for installing scmtools ..."
        mkdir -p $1
	if [ $? -ne 0 ];then
		echo "mkdir failed."
		exit 1
	fi
        SCMTOOLS_PATH=`readlink -f $1` 
        chmod 755 $SCMTOOLS_PATH
        echo "Create config file for scmtools"      
        createConFile
        echo "Downloading scmtools ..."
        if Install_client
        then
            :
        else
            echo "Fail to install scmtools"
            exit 1
        fi
        clean_ubuntu_env
        if [ -f "$SCMTOOLS_PATH/_scmtools/scmtools.sh" ]
        then
            echo "Install scmtools successfully."
            if [ `uname -o` != "Cygwin" ];then
                modify_path $SCMTOOLS_PATH
            fi
            exit 0  
        else
            echo "Fail to install scmtools"
            exit 1
        fi
} 

Main "$@"
