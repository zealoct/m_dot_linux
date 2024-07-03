#!/usr/bin/env python
#coding:gbk
#Copyright (c) Baidu.com, Inc. All Rights Reserved 
#author:zhangyan04(@baidu.com)

import sys
import string
import os
import SubProcess
import hashlib

PYTHON_HIGH_VERSION=False
if(sys.hexversion>0x020600F0):
    PYTHON_HIGH_VERSION=True

def call_command(cmd):
    p=SubProcess.Popen('_COMAKE2_SUBPROCESS= %s'%(cmd),
                       shell=True,
                       bufsize=0,
                       stdin=SubProcess.PIPE,
                       stdout=SubProcess.PIPE,
                       stderr=SubProcess.PIPE)
    (out,err)=p.communicate()
    return (p.returncode,
            out,
            err)

def Exclude(s,exs):
    ns=[]
    for x in s:
        if not x in exs:
            ns.append(x)
    return ns

def Unique(s,func=lambda x:x): 
    if(PYTHON_HIGH_VERSION):
        mask=set()
    else:
        import sets
        mask=sets.Set()
    ns=[]
    for x in s:
        key=func(x)
        if(not key in mask):
            mask.add(key)
            ns.append(x)
    return ns

def RedIt(s):
    if(sys.__stderr__.isatty()):
        return "\033[1;31;40m%s\033[0m"%(s)
    else:
        return s
    
def GreenIt(s):
    if(sys.__stderr__.isatty()):
        return "\033[1;32;40m%s\033[0m"%(s)
    else:
        return s

def InputChoice(prompt,choices):
    while(True):
        s=raw_input(prompt)
        s=string.lower(s)
        if(s and s[0] in choices):
            return s[0]

def ShortenWord(s,threshold=80):
    s=' '.join(string.split(s.replace("\\\n",' ')))
    if(len(s)<=threshold):
        return s
    else:
        return s[:threshold/2]+' ... '+s[-threshold/2:]

def FindFilesPredRecursive(p,recursive,pred):
    entries=os.listdir(p)
    files=[]
    for e in entries:
        pe=os.path.join(p,e)
        #ignore the version control files.
        if(e in ('.','..','.svn','CVS')):
            continue
        if(os.path.isdir(pe)):
            if(recursive):
                files.extend(FindFilesPredRecursive(pe,recursive,pred))
        elif(pred(pe)):
            files.append(os.path.normpath(pe))
    return files

def FindFilesPred(p,recursive,pred):
    return FindFilesPredRecursive(p,recursive,pred)

def FindFilesExts(p,recursive,exts):
    return FindFilesPred(p,recursive,lambda x:os.path.splitext(x)[1] in exts)

def CheckDirectoryModified(p,time_base):
    """检查目录是否发生修改.
    检查下面文件是否修改时间>time_base"""
    entries=os.listdir(p)
    for e in entries:
        pe=os.path.join(p,e)
        if(e in ('.','..','.svn','CVS')):
            continue
        if(os.path.isfile(pe)):
            mtime=os.stat(pe)[-2]
            if(mtime>time_base):
                return True
        if(os.path.isdir(pe)):
            tmp=CheckDirectoryModified(pe,time_base)
            if(tmp):
                return True
    return False

def GenMd5Sum(p):
    m = hashlib.md5()
    if(p.endswith('/')):
        strip_length=len(p)
    else:
        strip_length=len(p)+1
    _UpdateMd5(p,m,strip_length)
    return m.hexdigest()

def _UpdateMd5(p,m,strip_length):
    entries=os.listdir(p)
    entries.sort()
    for e in entries:
        pe=os.path.join(p,e)
        if(e in ('.','..','.svn','CVS','.COMAKE.BUILDED.TAG','.COMAKE.UPDATED.TAG')):
            continue
        if(os.path.isfile(pe)):
            m.update(pe[strip_length:])
        if(os.path.isdir(pe)):
            _UpdateMd5(pe,m,strip_length)
    return

def AddPrefixToBaseName(x,prefix):
    (dirname,basename)=os.path.split(x)
    return os.path.join(dirname,"%s%s"%(prefix,basename))

def ReplaceFileExtName(x,ext):
    (root,_)=os.path.splitext(x)
    return "%s%s"%(root,ext)

def AddFileExtName(x,ext):
    return "%s%s"%(x,ext)
