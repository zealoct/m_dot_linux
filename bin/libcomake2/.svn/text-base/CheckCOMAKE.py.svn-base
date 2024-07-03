#!/usr/bin/env python
import os
import pdb
import time
def getworkroot():
    f=open('./COMAKE')
    filelines=f.readlines()
    for i in filelines:
        if i.__contains__("WORKROOT"):
            if i.__contains__('\''):
                tmp=i.split('\'')
                workroot=tmp[1].strip()
            elif i.__contains__('"'):
                tmp=i.split('"')
                workroot=tmp[1].strip()
            break
    return workroot
def everypath(item,mainmodule):
    if item[0].__contains__('./svn'):
        value='False'
    elif item[0].__contains__(mainmodule):
        value='False'
    elif item[2].__contains__('COMAKE'):
        value=item[0]
    else:
        value='False'
    return value
def subcomake2(path,judge):
    currentpath=os.getcwd()
    try:
        os.chdir(path)
        if judge=='False':
            os.system('comake2 -P')
    except:
        print "[Falta]Using comake2 tools in :",path
    finally:
        os.chdir(currentpath)
        os.system('comake2 -B -J 8')
        cmd='rm -rf %s/.CheckCOMAKE'%(os.getenv('HOME'),)
        os.system(cmd)
def checksub(path):
    a=os.getenv('HOME')
    tmp=path.replace('../','%')
    filename=tmp.replace('/','#')
    pathfile='%s/.CheckCOMAKE/.%s'%(a,filename)
    folder='%s/.CheckCOMAKE'%(a,)
    if os.path.isdir(folder)==False:
        os.mkdir(folder)
    if os.path.exists(pathfile):
        value='True'
    else:
        os.mknod(pathfile)
        value='False'
    return value
def checkfile():
    a=os.getenv('HOME')
    modulepath=""
    path=a+'/.CheckCOMAKE'
    b=os.walk(path)
    for i in b :
        for item in i[2]:
            if item.__contains__('err-'):
                c=item.replace('#','/')
                c=c[5:]
                modulepath=getworkroot()+c
                print modulepath
                subcomake2(modulepath,'False')
    return modulepath
def submain():                
    workroot=getworkroot()
    tmpmodule=os.getcwd().split('/')[(workroot.count('/')-1):]
    mainmodule=""
    for i in tmpmodule:
        mainmodule=mainmodule+"/"+i
    print mainmodule
    if checksub('firsttime')=='False':
        cmd='find %s -name COMAKE'%(workroot,)
        walkpath=os.popen(cmd).read().split('\n')
        needmodule=[]
        for i in walkpath:
            if i.__contains__(mainmodule):
                print 'Main module need not compiler:',i
            else:
                needmodule.append(i)
        for i in needmodule:
            path=i[:-6] 
            subcomake2(path,checksub(path)) 
        cmd='rm -rf ~/.CheckCOMAKE'
        os.system(cmd)  
