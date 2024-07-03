#!/usr/bin/env python
import sys
import subprocess

if len(sys.argv) < 3:
    print "Usage: scan_zebu.py <username> <password>"
    exit(1)

username=sys.argv[1]
passwd=sys.argv[2]

ps={}
for k in range(23, 24):
    print "scan 172.{}.*.*".format(k)
    for i in range(232, 234):
        for j in range(0, 256):
            cmd="sshpass -p {} " \
                "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {}@172.{}.{}.{} " \
                "\"ls > /dev/null\"".format(passwd, username, k, i, j)
            #ps[(i, j)] = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            ps[j] = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for j in range(0, 256):
            ps[j].wait()
            if ps[j].returncode == 0:
                print "Found 172.{}.{}.{}".format(k, i, j)

#for i in range(232, 234):
#    for j in range(0, 256):
#        ps[(i, j)].wait()
#        if ps[(i, j)].returncode == 0:
#            print "Found 172.23.{}.{}".format(i, j)
