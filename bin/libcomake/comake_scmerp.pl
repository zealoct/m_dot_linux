#! /usr/bin/perl
use strict;
use Shell;

my $tool_path="$ENV{'HOME'}/.scmpf_tmp";
my $PID = getpgrp();
my $tool_name="$tool_path/autobuild$PID.pl";

`mkdir $tool_path`if (!(-d "$tool_path"));

#get script from scmpf
#`curl -s \"http://scmpf-server.baidu.com:8080/scmpf/page/getshell.do?ACTIONTYPE=getautocompilerscript\" >$tool_name`;
`curl -s \"http://scm.baidu.com/http/getautocompilerscript.action\" >$tool_name`;
#run
die("autobuild脚本获取失败，请联系scm!\n") if (-z $tool_name);
system ("perl $tool_name @ARGV");

#clear
`rm $tool_name`;
`find $tool_path/ -name "autobuild*" -mtime +1 -exec rm -f {} \\;`;  
exit(0);
