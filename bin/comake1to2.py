#!/usr/bin/env python
#coding:gbk 
#Copyright (c) Baidu.com, Inc. All Rights Reserved 
#author:zhangyan04(@baidu.com)

import sys
import string
import os

#����ԭ��comake1������.
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/libcomake/")

from cokparser import tarobj
from cokparser import cokparser

def top_handle(obj):
    xdict=obj.dict
    if("WORKROOT" in xdict):
        comake2.append('#����Ŀ¼')
        comake2.append("WORKROOT('%s')"%(xdict["WORKROOT"][0]))
    if("CPPFLAGS" in xdict):
        comake2.append('#CԤ�������')
        flag=' '.join(xdict["CPPFLAGS"])
        comake2.append("CPPFLAGS('%s')"%(flag))
    if("CFLAGS" in xdict):
        comake2.append('#C�������')
        flag=' '.join(xdict["CFLAGS"])
        comake2.append("CFLAGS('%s')"%(flag))
    if("CXXFLAGS" in xdict):
        comake2.append('#C++�������')
        flag=' '.join(xdict["CXXFLAGS"])
        comake2.append("CXXFLAGS('%s')"%(flag))
    if("INCPATH" in xdict):
        comake2.append('#ͷ�ļ�·��')
        flag=' '.join(xdict["INCPATH"])
        flag=string.replace(flag,'$(WORKROOT)','$')
        comake2.append("INCPATHS('%s')"%(flag))
    if("LINKFLAGS" in xdict):
        comake2.append('#���Ӳ���')
        flag=' '.join(xdict["LINKFLAGS"])
        comake2.append("LDFLAGS('%s')"%(flag))
    if("LDLIBS" in xdict):
        comake2.append('#���Ӳ���')
        flag=' '.join(xdict["LDLIBS"])
        comake2.append("LDFLAGS('%s')"%(flag))
    if("CONFIG" in xdict):
        comake2.append('#����ģ��')
        #����CONFIGS��������д�ÿ�.
        cfgs=xdict["CONFIG"]
        for cfg in cfgs:
            if(cfg=="MAKDEP"):
                continue
            if(cfg.find("(")==-1):
                comake2.append("CONFIGS('%s')"%(cfg))
            else:
                ps=string.split(cfg,'(')
                comake2.append("CONFIGS('%s@%s')"%(ps[0],ps[1][:-1]))
    #Դ�ļ�.
    if("SOURCES" in xdict):
        src=' '.join(xdict["SOURCES"])
        #ʹ��user_sources�����������.
        comake2.append('#����Դ�ļ�')
        comake2.append("user_sources='%s'"%(src))
    
    #Ȼ����Ҫ�����������Ŀ��.
    for tar in obj.tarlst:
        sub_handle(tar)
    return 

def sub_handle(obj):
    name=obj.name
    xdict=obj.dict
    tplt='app'
    if('TEMPLATE' in xdict):
        tplt=xdict['TEMPLATE'][0]
    srcs=''
    if('SOURCES' in xdict):
        srcs=' '.join(xdict['SOURCES'])
    if(tplt=='lib'):
        name=name[3:-2]
        comake2.append('#��̬��')
        if(not srcs):
            comake2.append("StaticLibrary('%s',Sources(user_sources))"%name)
        else:
            comake2.append("StaticLibrary('%s',Sources('%s'))"%(name,srcs))
    elif(tplt=='so'):
        name=name[3:-3]
        comake2.append('#�����')
        if(not srcs):
            comake2.append("SharedLibrary('%s',Sources(user_sources))"%name)
        else:
            comake2.append("SharedLibrary('%s',Sources('%s'))"%(name,srcs))
    elif(tplt=='sub'):
        comake2.append('#��Ŀ¼')
        comake2.append("Directory('%s')"%name)
    elif(tplt=='app'):
        comake2.append('#Ӧ�ó���')
        if(not srcs):
            comake2.append("Application('%s',Sources(user_sources))"%name)
        else:
            comake2.append("Application('%s',Sources('%s'))"%(name,srcs))
    return 


p=cokparser()
p.cc(open(sys.argv[1]).read())
comake2=[]
comake2.append('#edit-mode: -*- python -*-')
comake2.append('#coding:gbk')
comake2.append('')

top_handle(p.root)
#д�����ļ�.
open('COMAKE.comake1','w').writelines(map(lambda x:'%s\n'%x,comake2))
