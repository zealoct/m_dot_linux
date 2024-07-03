#!/usr/bin/python

import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/libcomake/");

COVERSION = "1.0.1";
COVERFLAG = "COMAKE_VERSION";
WORKROOT = "WORKROOT";
TEMPLATE = "TEMPLATE";
CPPSRC = "CPPSRC";
IDLCOMP = "IDLCC";
IDLSRC = "IDLSRC";
SUBMK = "SUBMK";
TESTMK = "TESTMK";
INCPATH = "INCPATH";
LIBDEP = "LIBDEP";
LDLIBS = "LDLIBS";
LINK = "LINK";
CONFIG = "CONFIG";
INSTALLPATH = "INSTALLPATH";
OTHERTARGETS = "OTHERTARGETS";
TPLFLAG = ['sub', 'app', 'lib', 'so', 'no'];

DIRSRC = "src";
DIRTEST = "unittest";
DIRCONF = "conf";
FILEREADME = "README";
FILECHANGELOG = "ChangeLog";
VERSION = "VERSION";
CHECKOUT = False;
TARGET = "target";
TEST = "test";
CPLOBJ = [TARGET, TEST];
LINUX32 = "linux32";
LINUX64 = "linux64";
DEBUGSCOPE = "debug";
AUTOGEN = "comake_autogen";

IS_32 = os.popen("uname -i 2>/dev/null").read().strip() != "x86_64";
IS_64 = os.popen("uname -i 2>/dev/null").read().strip() == "x86_64";

DEBUG = 0;

SCMPFURL="http://scm.baidu.com/http/getautocompilerscript.action";
#SCMPFURL = "http://scmpf-server.baidu.com:8080/scmpf/page/getshell.do?ACTIONTYPE=getautocompilerscript";

MAKDEP = "MAKDEP";
IDLNODIR = "IDLNODIR";
CFGSKIP = [MAKDEP, IDLNODIR];

def debug_log(text):
	if DEBUG:
		print "---DEBUG:	"+str(text);


def warning_log(text):
	print "---WARNING:	"+text;
