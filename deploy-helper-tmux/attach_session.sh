#!/bin/bash

# File Name: attach_session.sh
# Author: hanjinchen@baidu.com
#
# Attach to a TMUX session specified by session_num

if [ $# -lt 1 ]; then
    echo "usage: attach_session.sh session_num"
    echo "       attach to a TMUX session specified by session_num"
    exit 0
fi

socket_name="tmux-online-deploy-$USER"
TMUX="$PWD/tmux -f $PWD/tmux.conf -L $socket_name "

session_name=$1"-online-deploy-session"

$TMUX attach -dt $session_name
