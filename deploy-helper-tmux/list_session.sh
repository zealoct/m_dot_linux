#!/bin/bash

# File Name: list_session.sh
# Author: hanjinchen@baidu.com
#
# List all TMUX online deploy sessions under this user

socket_name="tmux-online-deploy-$USER"
TMUX="$PWD/tmux -f $PWD/tmux.conf -L $socket_name "

$TMUX ls
