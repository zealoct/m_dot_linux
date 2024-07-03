#!/bin/bash

# File Name: connect_server.sh
# Author: hanjinchen@baidu.com
#
# Send commands to windows in a TMUX session opened by connect_server.sh
# Note: Put TMUX window_id (starts with '@', like '@0', '@1') into exclude file
#
# EXAMPLE
# Session Name: 2-online-deploy-session
# Session Num: 2
# Command file name: cmd-ls
# ls -l
#
# Exclude file: EX
# @2
#
# ./sendcmd.sh 2 cmd-ls EX

set -ue

if [ $# -lt 2 ]; then
    echo "usage: sendcmd.sh session_num cmd_file [exclude_file]"
    echo "       send command in cmd_file to the specific TMUX session created by"
    echo "       connect_server.sh with session number session_num. You could put some TMUX"
    echo "       window_ids (not window_index!) into one exclude_file, this script will skip"
    echo "       the corresponding window when sending commands"
    exit 0
fi

session_name_suffix="-online-deploy-session"
session_num=$1
session_name=$session_num$session_name_suffix
cmd=`head -n 1 $2`
exclude_window_ids=''

if [ $# -ge 3 ]; then
    if [ ! -e $3 ]; then
        echo "Specified exclude file does not exists!"
        break
    fi

    exclude_window_ids=`cat $3`
fi

# Specify a per-user socket for the tmux, thus the online deploy session of one user will not
# effect session of another user
socket_name="tmux-online-deploy-$USER"
TMUX="$PWD/tmux -f $PWD/tmux.conf -L $socket_name "

echo "*****************************"
echo "Cmd:     '$cmd'"
echo "Socket:  "$socket_name
echo "Session: "$session_name
echo "*****************************"

windows=`$TMUX list-windows -t $session_name -F '#{window_id}'`
for window in $windows; do
    send_flag=true
    for exclude_id in $exclude_window_ids; do
        if [ $window = $exclude_id ]; then
            send_flag=false
            break
        fi
    done

    if [ $send_flag = true ]; then
        $TMUX select-window -t $window
        $TMUX send-keys -t $session_name "$cmd" C-m
    fi
done
