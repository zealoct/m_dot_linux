#!/bin/bash

# File Name: connect_server.sh
# Author: hanjinchen@baidu.com
#
# Parse the hosts file, each line in this file should hold the host name of one remote server,
# this script will automatically start a TMUX session, and create one window for each remote
# server, and automatically ssh to the remote server with the login name and password specified
# by the user using *sshpass*.
#
# The TMUX session name has the form "session_num-online-deploy-session", where session_num will be
# auto-selected from 1. The TMUX window name has the form "#{window_id}#{window_name}", if your
# window name is not like this (check the status line), maybe it's your shell who changed your
# window name.
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
#
# $ ./connect_server.sh hosts hanjinchen hjc123

set -ue

if [ $# -lt 3 ]; then
    echo "usage: connect_server.sh hosts_file login_name password"
    echo "       Automatically start a tmux session, for each host in hosts_file, create a tmux"
    echo "       window in the session to ssh to it."
    exit 0
fi

hosts_file=$1
login_name=$2
passwd=$3

echo "hosts_file:"$hosts_file
echo "login:passwd=$login_name:$passwd"

if [ ! -e $hosts_file ]; then
    echo "hosts_file does not exists!"
    exit 0
fi

# Specify a per-user socket for the tmux, thus the online deploy session of one user will not
# effect session of another user
socket_name="tmux-online-deploy-$USER"
TMUX="$PWD/tmux -f $PWD/tmux.conf -L $socket_name "

# Use a temporary ssh config file with "StrictHostKeyChecking no" and "UserKnownHostsFile /dev/null"
# or else the ssh will ask user to confirm the host's rsa key if the host is connected the first
# time, which will break the automatic login.
#
# But be aware that disabling StrictHostKeyChecking is INSECURE, and this will not effect the
# system's ssh config file
SSH="ssh -F $PWD/ssh.config"

# This must be done, otherwise there will be "bad permission" error when ssh
chmod 600 $PWD/ssh.config

# Search for an unoccupied $session_num
session_name_suffix="-online-deploy-session"
session_num=1
while true
do
    $TMUX has-session -t $session_num$session_name_suffix 2> /dev/null || break
    session_num=$(($session_num+1))
done
session_name=$session_num$session_name_suffix

echo "*****************************"
echo "Socket:       "$socket_name
echo "Session Name: "$session_name
echo "Session Num:  "$session_num
echo "*****************************"

$TMUX new-session -d -s $session_name

create_new_window=false
hosts=`cat $hosts_file`
for host in $hosts
do
    echo "Connecting to "$host
    if [ $create_new_window = true ]; then
        $TMUX new-window -t $session_name
    else
        create_new_window=true
    fi

    gid=`$TMUX list-windows -t $session_name -F '#{window_id}' | tail -n 1`
    $TMUX rename-window -t $gid "$gid:$host"
    $TMUX send-keys -t $session_name "$PWD/sshpass -p $passwd $SSH $login_name@$host" C-m
done
