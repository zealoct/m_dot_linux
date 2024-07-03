#!/usr/bin/env python
#coding:gbk
#Copyright (c) Baidu.com, Inc. All Rights Reserved 
#author:zhangyan04(@baidu.com)

import os
import string
import glob

"""
将这个功能放在一个全新的文件原因,
是因为这个功能现在还比较简单,但是以后可能会相对来说更加复杂.
更加智能一些.
"""


#生成COMAKE文件模板.
COMAKE_TEMPLATE="""#edit-mode: -*- python -*-
#coding:gbk

#工作路径.
WORKROOT(%(workroot)s)

#使用硬链接copy.
CopyUsingHardLink(True)

#支持32位/64位平台编译
#ENABLE_MULTI_LIBS(True)

#C预处理器参数.
CPPFLAGS('-D_GNU_SOURCE -D__STDC_LIMIT_MACROS -DVERSION=\\\\\\"1.9.8.7\\\\\\"')
#为32位目标编译指定额外的预处理参数
#CPPFLAGS_32('-D_XOPEN_SOURE=500')

#C编译参数.
CFLAGS('-g -pipe -W -Wall -fPIC')

#C++编译参数.
CXXFLAGS('-g -pipe -W -Wall -fPIC')

#IDL编译参数
IDLFLAGS('--compack')

#UBRPC编译参数
UBRPCFLAGS('--compack')

#头文件路径.
INCPATHS('. ./include ./output ./output/include')

#使用库
#LIBS('./lib%(module)s.a')

#链接参数.
LDFLAGS('-lpthread -lcrypto -lrt')

#依赖模块
%(configs)s

#为32位/64位指定不同的依赖路径.
#CONFIGS_32('lib2/ullib')
#CONFIGS_64('lib2-64/ullib')

user_sources=%(sources)s
user_headers=%(headers)s

#可执行文件
#Application('%(module)s',Sources(user_sources))
#静态库
#StaticLibrary('%(module)s',Sources(user_sources),HeaderFiles(user_headers))
#共享库
#SharedLibrary('%(module)s',Sources(user_sources),HeaderFiles(user_headers))
#子目录
#Directory('demo')

"""

def scratch(env,rev=''):
    """从头建立一个新的COMAKE"""
    
    #能够根据目录名判断CVS.
    topnames=["app",
              "appdemo",
              "app-test",
              "com",
              "com-test",
              "eb",
              "erp",
              "fe",
              "general-test",
              "ibase",
              "is",
              "iit",
              "inf",
              "iit-test",
              "lib2",
              "lib2-64",
              "libsrc",
              "op",
              "pe",
              "ps",
              "portal",
              "ps-test",
              "psdemo",
              "public",
              "quality",
              "sys",
              "third",
              "third-64",
              "third-src",
              "ullib-test",
              "opencode",
              "ue",
              "st",
              "home"]

    cwd=os.getcwd()
    ps=string.split(cwd,'/')
    workroot=cwd
    cvspath=cwd
    for i in range(len(ps)-1,-1,-1):
        if(ps[i] in topnames):
            back=len(ps)-i
            workroot='../'*back
            cvspath='/'.join(ps[i:])
            break
    workroot="'%s'"%(workroot)
    module=os.path.basename(cwd)

    #找出所有的源文件以及头文件.
    sources=glob.glob('*.cpp')
    sources+=glob.glob('*.c')
    sources+=glob.glob('*.cc')
    sources+=glob.glob('*.idl')
    sources="'%s'"%(' '.join(sources))
    
    headers=glob.glob('*.h')
    headers+=glob.glob('*.hpp')
    headers="'%s'"%(' '.join(headers))
    
    #检测依赖模块,代码和依赖都取基线.
    #如果没有取成功的话,那么默认使用lib2/ullib来使用.
    configs=env.GenConfigsForCOMAKE(cvspath,'',rev)
    if(not configs):
        if rev=='':
            msg='可能的原因：1.平台无基线版本；或2.没有在模块路径下执行命令'
            env.LogSystem().LogWarning('没有取到最新基线的依赖，默认使用lib2/ullib的依赖\n%s'%msg)
        else:
            msg='可能的原因：1.平台无版本%s；或2.没有在模块路径下执行命令'%rev
            env.LogSystem().LogWarning('没有取到版本%s的依赖，默认使用lib2/ullib的依赖\n%s'%(rev,msg))
        configs="CONFIGS('lib2/ullib')"
        
    #如果存在COMAKE,那么保存原来老的,新生成的叫做COMAKE.scratch
    #如果不存在的话,那么直接生成COMAKE
    filename='COMAKE'
    if(os.path.exists('COMAKE')):
        filename='COMAKE.scratch'
    open(filename,'w').write(COMAKE_TEMPLATE%(locals()))
