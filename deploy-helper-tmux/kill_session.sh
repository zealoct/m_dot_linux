#!/bin/bash

# File Name: kill_session.sh
# Author: hanjinchen@baidu.com
#
# Kill a TMUX session specified by session_num

if [ $# -lt 1 ]; then
    echo "usage: kill_session.sh session_num"
    echo "       kill a TMUX session specified by session_num"
    exit 0
fi

socket_name="tmux-online-deploy-$USER"
TMUX="$PWD/tmux -f $PWD/tmux.conf -L $socket_name "

session_name=$1"-online-deploy-session"

$TMUX kill-session -t $session_name
