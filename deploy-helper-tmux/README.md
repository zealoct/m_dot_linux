# Readme

## Why TMUX

1. Similar to Screen, but I am not familiar with Screen
1. Can survive the network disconnect
1. Easy to use
1. Window can be split into multiple panels

## How to use

### Preparation

**File Name** hosts

    hostname1
    hostname2
    hostname3

**Login Name** hanjinchen

**Login Password** hjc123

**File Name** cmd-ls

    ls -l

### Steps

1.  `$ ./connect_server.sh hosts hanjinchen hjc123`

        *****************************
        Socket:        tmux-online-deploy-hanjinchen
        Session:       1-online-deploy-session
        Session Num:  1
        *****************************

1.  `$ ./list_session.sh`

        1-online-deploy-session: 15 windows (created Mon Oct 12 13:02:28 2015) [170x34]

1.  `$ ./attach_session 1`

    Use `Alt+n` and `Alt+p` to navigate between windows, check whether the connections has succeed

    if window with id @2 fails, make an EX file

    **File Name** EX

        @2

    Otherwise, the EX file is not necesseary

1.  Use ``` d`` in any TMUX window to detach

1.  Send cmd to all(or part of) windows in a session using `$ ./sendcmd.sh 1 cmds/cmd-ls EX`

1.  Attach to check the execution result, and detach to send command

1.  `$ ./sendcmd.sh 1 cmds/cmd-exit` or `$ ./kill_session.sh 1` to exit

More details, please check the comments in *connect_server.sh*, *sendcmd.sh* and *tmux.conf*
