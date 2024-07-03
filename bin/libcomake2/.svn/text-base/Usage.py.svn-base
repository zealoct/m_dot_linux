#!/usr/bin/env python
#coding:gbk
#Copyright (c) Baidu.com, Inc. All Rights Reserved 
#author:zhangyan04(@baidu.com)

import os

#读取版本号信息.
VERSION=int(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              'COMAKE.VERSION')).read())

#帮助信息.
HELP="""comake[com make]能够自动帮助用户搭建环境,并且生成Makefile工具.
程序会读取目录下面的COMAKE文件,产生Makefile和环境.用户需要提供这个COMAKE文件.
版本:%d
参数:
        -h --help 查看帮助
        -D --debug 开启debug选项[默认不打开].-D -D可以查看更多调试信息.
        -S --scratch 创建一个默认的COMAKE文件
        -E --export-configs 导出模块的4位版本依赖,存放在COMAKE.CONFIGS下面.比如-E public/ub@1.0.0.0
        -W --watch-configs 查看本地依赖模块.-W -W可以查看模块引入来源.-W -W -W可以查看依赖模块的依赖.
        -I --import-files 在解释COMAKE文件之前导入模块
        -C --change directory 切换到directory下面执行[默认当前目录]
        -Q --quiet 安静模式[默认不打开]
        --32 生成32位下面的Makefile[默认不打开]
        -U --update-configs 更新环境
        -B --build-configs 构建环境
        -F --force 更新/构建环境时强制进行[默认不打开]
        -J --make-thread-number 如果模块使用COMAKE生成的Makefile的话,编译线程数
        -K --keep-going 构建/更新环境中途出错的话,忽略错误继续[默认不打开]
        --no-recursive 不递归生成每个目录下面的Makefile[默认情况下是递归生成]
"""
def usage():
    print HELP%(VERSION)
    
