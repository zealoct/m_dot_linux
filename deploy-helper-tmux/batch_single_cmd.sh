#!/bin/bash

# File Name: batch_single_cmd.sh
# Author: hanjinchen@baidu.com
#
# Parse the hosts file, each line in this file should hold the host name of one remote server,
# this script will automatically send cmd to each host
#
# EXAMPLE
#
# file name: hosts
# hostname1
# hostname2
# hostname3
#
# login name: hanjinchen
# login password: hjc123
# cmd: ls
#
# $ ./batch_single_cmd.sh hosts hanjinchen hjc123 ls

set -u

if [ $# -lt 4 ]; then
    echo "usage: connect_server.sh hosts_file login_name password command"
    echo "       Automatically send command to each host in hosts_file"
    exit 0
fi

hosts_file=$1
login_name=$2
passwd=$3
cmd=$4

echo "hosts_file:"$hosts_file
echo "login:passwd=$login_name:$passwd"

if [ ! -e $hosts_file ]; then
    echo "hosts_file does not exists!"
    exit 0
fi

# Use a temporary ssh config file with "StrictHostKeyChecking no" and "UserKnownHostsFile /dev/null"
# or else the ssh will ask user to confirm the host's rsa key if the host is connected the first
# time, which will break the automatic login.
#
# But be aware that disabling StrictHostKeyChecking is INSECURE, and this will not effect the
# system's ssh config file
SSH="ssh -F $PWD/ssh.config"

# This must be done, otherwise there will be "bad permission" error when ssh
chmod 600 $PWD/ssh.config

hosts=`cat $hosts_file`
for host in $hosts
do
    $PWD/sshpass -p $passwd $SSH $login_name@$host $cmd
done
