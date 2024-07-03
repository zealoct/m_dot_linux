#!/usr/bin/env python
#coding:gbk
#Copyright (c) Baidu.com, Inc. All Rights Reserved 
#author:zhangyan04(@baidu.com)

import os
import string
import glob

"""
��������ܷ���һ��ȫ�µ��ļ�ԭ��,
����Ϊ����������ڻ��Ƚϼ�,�����Ժ���ܻ������˵���Ӹ���.
��������һЩ.
"""


#����COMAKE�ļ�ģ��.
COMAKE_TEMPLATE="""#edit-mode: -*- python -*-
#coding:gbk

#����·��.
WORKROOT(%(workroot)s)

#ʹ��Ӳ����copy.
CopyUsingHardLink(True)

#֧��32λ/64λƽ̨����
#ENABLE_MULTI_LIBS(True)

#CԤ����������.
CPPFLAGS('-D_GNU_SOURCE -D__STDC_LIMIT_MACROS -DVERSION=\\\\\\"1.9.8.7\\\\\\"')
#Ϊ32λĿ�����ָ�������Ԥ�������
#CPPFLAGS_32('-D_XOPEN_SOURE=500')

#C�������.
CFLAGS('-g -pipe -W -Wall -fPIC')

#C++�������.
CXXFLAGS('-g -pipe -W -Wall -fPIC')

#IDL�������
IDLFLAGS('--compack')

#UBRPC�������
UBRPCFLAGS('--compack')

#ͷ�ļ�·��.
INCPATHS('. ./include ./output ./output/include')

#ʹ�ÿ�
#LIBS('./lib%(module)s.a')

#���Ӳ���.
LDFLAGS('-lpthread -lcrypto -lrt')

#����ģ��
%(configs)s

#Ϊ32λ/64λָ����ͬ������·��.
#CONFIGS_32('lib2/ullib')
#CONFIGS_64('lib2-64/ullib')

user_sources=%(sources)s
user_headers=%(headers)s

#��ִ���ļ�
#Application('%(module)s',Sources(user_sources))
#��̬��
#StaticLibrary('%(module)s',Sources(user_sources),HeaderFiles(user_headers))
#�����
#SharedLibrary('%(module)s',Sources(user_sources),HeaderFiles(user_headers))
#��Ŀ¼
#Directory('demo')

"""

def scratch(env,rev=''):
    """��ͷ����һ���µ�COMAKE"""
    
    #�ܹ�����Ŀ¼���ж�CVS.
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

    #�ҳ����е�Դ�ļ��Լ�ͷ�ļ�.
    sources=glob.glob('*.cpp')
    sources+=glob.glob('*.c')
    sources+=glob.glob('*.cc')
    sources+=glob.glob('*.idl')
    sources="'%s'"%(' '.join(sources))
    
    headers=glob.glob('*.h')
    headers+=glob.glob('*.hpp')
    headers="'%s'"%(' '.join(headers))
    
    #�������ģ��,�����������ȡ����.
    #���û��ȡ�ɹ��Ļ�,��ôĬ��ʹ��lib2/ullib��ʹ��.
    configs=env.GenConfigsForCOMAKE(cvspath,'',rev)
    if(not configs):
        if rev=='':
            msg='���ܵ�ԭ��1.ƽ̨�޻��߰汾����2.û����ģ��·����ִ������'
            env.LogSystem().LogWarning('û��ȡ�����»��ߵ�������Ĭ��ʹ��lib2/ullib������\n%s'%msg)
        else:
            msg='���ܵ�ԭ��1.ƽ̨�ް汾%s����2.û����ģ��·����ִ������'%rev
            env.LogSystem().LogWarning('û��ȡ���汾%s��������Ĭ��ʹ��lib2/ullib������\n%s'%(rev,msg))
        configs="CONFIGS('lib2/ullib')"
        
    #�������COMAKE,��ô����ԭ���ϵ�,�����ɵĽ���COMAKE.scratch
    #��������ڵĻ�,��ôֱ������COMAKE
    filename='COMAKE'
    if(os.path.exists('COMAKE')):
        filename='COMAKE.scratch'
    open(filename,'w').write(COMAKE_TEMPLATE%(locals()))
