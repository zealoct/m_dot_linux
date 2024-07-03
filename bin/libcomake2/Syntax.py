#!/usr/bin/env python
#coding:gbk
#Copyright (c) Baidu.com, Inc. All Rights Reserved 
#author:zhangyan04(@baidu.com)

import os
import string

import Environment
import SyntaxTag
import Target

def WORKROOT(s):
    env=Environment.GetCurrent()
    env.SetWorkRoot(s)
    cwd=os.path.abspath(os.getcwd())
    topdir=os.path.abspath(os.path.join(cwd,env.WorkRoot()))
    cvspath=cwd[len(topdir)+1:]
    env.SetCVSPath(cvspath)

def CVSPATH(s):    
    env=Environment.GetCurrent()
    env.SetCVSPath(s)
    workroot='/'.join(('..')*len(string.split(s,'/')))
    env.SetWorkRoot(workroot)

def MakeThreadNumber(k):
    pass

def VERSION(k):
    env=Environment.GetCurrent()
    env.SetVersion(k)

def CopyUsingHardLink(k):
    env=Environment.GetCurrent()
    env.SetCopyUsingHardLink(k)

def _is_64bits():
    env=Environment.GetCurrent()
    return env.Bit() == '64'

def CC(k):
    env=Environment.GetCurrent()
    env.SetCc(k)

def CC_64(k):
    if _is_64bits():
        CC(k)

def CC_32(k):
    if not _is_64bits():
        CC(k)

def CXX(k):
    env=Environment.GetCurrent()
    env.SetCxx(k)

def CXX_64(k):
    if _is_64bits():
        CXX(k)

def CXX_32(k):
    if not _is_64bits():
        CXX(k)

def CppFlags(*ss):
    tag=SyntaxTag.TagCppFlags()
    tag.AddVs(ss)
    return tag

def CPPFLAGS(*ss):
    env=Environment.GetCurrent()
    env.CppFlags().AddVs(ss)

def CPPFLAGS_64(*ss):
    if _is_64bits():
        CPPFLAGS(*ss)
        
def CPPFLAGS_32(*ss):
    if not _is_64bits():
        CPPFLAGS(*ss)

def ENABLE_MULTI_LIBS(k):
    env=Environment.GetCurrent()
    env.SetMultilibs(k)
    
def CFlags(*ss):
    tag=SyntaxTag.TagCFlags()
    tag.AddVs(ss)
    return tag

def CFLAGS(*ss):
    env=Environment.GetCurrent()
    env.CFlags().AddVs(ss)

def CFLAGS_64(*ss):
    if _is_64bits():
        CFLAGS(*ss)

def CFLAGS_32(*ss):
    if not _is_64bits():
        CFLAGS(*ss)

def CxxFlags(*ss):
    tag=SyntaxTag.TagCxxFlags()
    tag.AddVs(ss)
    return tag

def CXXFLAGS(*ss):
    env=Environment.GetCurrent()
    env.CxxFlags().AddVs(ss)
    
def CXXFLAGS_64(*ss):
    if _is_64bits():
        CXXFLAGS(*ss)

def CXXFLAGS_32(*ss):
    if not _is_64bits():
        CXXFLAGS(*ss)

def _IncludePaths(tag,ss):
    for s in ss:
        ps=string.split(s)
        for x in ps:
            if(x[0]=='$'):
                env=Environment.GetCurrent()
                x='%s%s'%(env.WorkRoot(),
                          x[1:])
                x=os.path.normpath(x)
            tag.AddSV(x)
    return tag

def IncludePaths(*ss):
    tag=SyntaxTag.TagIncludePaths()
    return _IncludePaths(tag,ss)

def INCPATHS(*ss):
    env=Environment.GetCurrent()
    _IncludePaths(env.IncludePaths(),
                  ss)

def INCPATHS_64(*ss):
    if _is_64bits():
        INCPATHS(*ss)

def INCPATHS_32(*ss):
    if not _is_64bits():
        INCPATHS(*ss)

def Libraries(*ss):
    tag=SyntaxTag.TagLibraries()
    tag.AddVs(ss)
    return tag

def LIBS(*ss):
    env=Environment.GetCurrent()
    env.Libraries().AddVs(ss)

def LIBS_64(*ss):
    if _is_64bits():
        LIBS(*ss)

def LIBS_32(*ss):
    if not _is_64bits():
        LIBS(*ss)

def LinkFlags(*ss):
    tag=SyntaxTag.TagLinkFlags()
    tag.AddVs(ss)
    return tag

def LDFLAGS(*ss):
    env=Environment.GetCurrent()
    env.LinkFlags().AddVs(ss)

def LDFLAGS_64(*ss):
    if _is_64bits():
        LDFLAGS(*ss)

def LDFLAGS_32(*ss):
    if not _is_64bits():
        LDFLAGS(*ss)

def IdlFlags(*ss):
    tag=SyntaxTag.TagIdlFlags()
    tag.AddVs(ss)
    return tag

def IDLFLAGS(*ss):
    env=Environment.GetCurrent()
    env.IdlFlags().AddVs(ss)
    
def IDLFLAGS_64(*ss):
    if _is_64bits():
        IDLFLAGS(*ss)

def IDLFLAGS_32(*ss):
    if not _is_64bits():
        IDLFLAGS(*ss)

def UbRpcFlags(*ss):
    tag=SyntaxTag.TagUbRpcFlags()
    tag.AddVs(ss)
    return tag

def UBRPCFLAGS(*ss):
    env=Environment.GetCurrent()
    env.UbRpcFlags().AddVs(ss)

def UBRPCFLAGS_64(*ss):
    if _is_64bits():
        UBRPCFLAGS(*ss)

def UBRPCFLAGS_32(*ss):
    if not _is_64bits():
        UBRPCFLAGS(*ss)

def PROTOFLAGS(*ss):
    env=Environment.GetCurrent()
    env.ProtoFlags().AddVs(ss)

def EXPORTS(*ss):
    env=Environment.GetCurrent()
    tag=SyntaxTag.TagVector()
    tag.AddVs(ss)
    env.SetExports(tag.V())
    
import glob
def GLOB(*ss):
    strs=[]
    for s in ss:
        ps=string.split(s)
        for p in ps:
            gs=glob.glob(p)
            gs.sort()
            strs.extend(gs)
    return ' '.join(strs)


def _ParseNameAndArgs(*ss):
    args=[]
    names=[]
    for s in ss:
        if(isinstance(s,str)):
            names.extend(string.split(string.strip(s)))
        else:
            args.append(s)
    return (names,args)

def DisBuild(k=True):
    tag=SyntaxTag.TagDisableBuild()
    tag.SetV(k)
    return tag

def BuildCmd(k):
    tag=SyntaxTag.TagBuildCmd()
    tag.SetV(k)
    return tag

def CONFIGS(*ss):
    env=Environment.GetCurrent()
    (names,args)=_ParseNameAndArgs(*ss)
    for name in names:
        (cvspath,codetag,revision,depstag,buildcmd,status)=env.SCMSystem().ParseConfig(name)
        env.CreateConfigFromArgs(cvspath,
                                 codetag,
                                 revision,
                                 depstag,
                                 args,buildcmd,status)

def CONFIGS_64(*ss):
    if _is_64bits():
        CONFIGS(*ss)

def CONFIGS_32(*ss):
    if not _is_64bits():
        CONFIGS(*ss)

def Sources(*ss):
    env=Environment.GetCurrent()
    (names,args)=_ParseNameAndArgs(*ss)
    tag=SyntaxTag.TagSources()
    for name in names:
        src=env.CreateSource(name,args)
        tag.AddSV(src)
    return tag

def CCPSources(*ss):
    env=Environment.GetCurrent()
    (names,args)=_ParseNameAndArgs(*ss)
    tag=SyntaxTag.TagSources()
    for name in names:
        src=env.CreateCCPSource(name,args)
        tag.AddSV(src)
    return tag

def RUNCCP(name,*args):
    _Target(name,
            Target.RUNCCP.TYPE,
            args)

def CCPDriver(v):
    tag=SyntaxTag.TagCCPDriver()
    tag.SetV(v)
    return tag

def CCPFlags(*ss):
    tag=SyntaxTag.TagCCPFlags()
    tag.AddVs(ss)
    return tag

def CCPUseIncPaths(v):
    tag=SyntaxTag.TagCCPUseIncPaths()
    tag.SetV(v)
    return tag

def PCLINTDRIVER(k):
    env=Environment.GetCurrent()
    env.SetPclintDriver(k)

def PCLINTFLAGS(k):
    env=Environment.GetCurrent()
    env.SetPclintFlags(k)

def CCHECKDRIVER(k):
    env=Environment.GetCurrent()
    env.SetCcheckDriver(k)

def CCHECKFLAGS(k):
    env=Environment.GetCurrent()
    env.SetCcheckFlags(k)

def CCPTARGET(k):
    env=Environment.GetCurrent()
    env.SetCcpTarget(k)

def CCP_DRIVER(k):
    env=Environment.GetCurrent()
    env.SetCcpDriver(k)

def CCP_FLAGS(k):
    env=Environment.GetCurrent()
    env.SetCcpFlags(k)

def ShellCommands(*ss):
    tag=SyntaxTag.TagShellCommands()
    tag.AddSVs(ss)
    return tag

def CleanCommands(*ss):
    tag=SyntaxTag.TagCleanCommands()
    tag.AddSVs(ss)
    return tag

def CleanFiles(*ss):
    tag=SyntaxTag.TagCleanFiles()
    tag.AddVs(ss)
    return tag

def Prefixes(*ss):
    tag=SyntaxTag.TagPrefixes()
    tag.AddVs(ss)
    return tag

def Depends(*ss):
    tag=SyntaxTag.TagPrefixes()
    tag.AddVs(ss)
    return tag

def _Target(name,type,args):
    env=Environment.GetCurrent()
    env.CreateTarget(name,type,args)

def Application(name,*args):
    _Target(name,
            Target.Application.TYPE,
            args)

def Application_64(name,*args):
    if _is_64bits():
        Application(name,*args)

def Application_32(name,*args):
    if not _is_64bits():
        Application(name,*args)

def OutputPath(k):
    tag=SyntaxTag.TagOutputPath()
    tag.SetV(k)
    return tag

def StaticLibrary(name,*args):
    _Target(name,
            Target.StaticLibrary.TYPE,
            args)

def StaticLibrary_64(name,*args):
    if _is_64bits():
        StaticLibrary(name,*args)

def StaticLibrary_32(name,*args):
    if not _is_64bits():
        StaticLibrary(name,*args)

def HeaderOutputPath(k):
    tag=SyntaxTag.TagHeaderOutputPath()
    tag.SetV(k)
    return tag

def HeaderFiles(*ss):
    tag=SyntaxTag.TagHeaderFiles()
    tag.AddVs(ss)
    return tag

def LinkDeps(k):
    tag=SyntaxTag.TagLinkDepsFlags()
    tag.SetV(k)
    return tag

def _LinkLibs(tag,ss):
    for s in ss:
        ps=string.split(s)
        for x in ps:
            if(x[0]=='$'):
                env=Environment.GetCurrent()
                x='%s%s'%(env.WorkRoot(),
                          x[1:])
                x=os.path.normpath(x)
            tag.AddSV(x)
    return tag

def LinkLibs(*ss):
    tag=SyntaxTag.TagLinkLibs()
    return _LinkLibs(tag,ss)

def WholeArchives(*ss):
    tag=SyntaxTag.TagWholeArchiveLibs()
    tag.AddVs(ss)
    return tag

def SharedLibrary(name,*args):
    _Target(name,
            Target.SharedLibrary.TYPE,
            args)

def SharedLibrary_64(name,*args):
    if _is_64bits():
        SharedLibrary(name,*args)

def SharedLibrary_32(name,*args):
    if not _is_64bits():
        SharedLibrary(name,*args)

def NovaTestStub(name,*args):
    _Target(name,
            Target.NovaTestStub.TYPE,
            args)

def Directory(name,*args):    
#    env=Environment.GetCurrent()
#   env.LogSystem().LogNotice(
#         "syntax 'Directory' is deprecated,use 'SubDirectory' instead")
    SubDirectory(name,*args)

def Directory_64(name,*args):    
    if _is_64bits():
        Directory(name,*args)

def Directory_32(name,*args):    
    if not _is_64bits():
        Directory(name,*args)

def SubDirectory(name,*args):
    env=Environment.GetCurrent()
    env.AppendSubDirectory(os.path.normpath(name))
    _Target(name,
            Target.SubDirectory.TYPE,
            args)
    
def TARGET(name,*args):
    _Target(name,
            Target.FuzzTarget.TYPE,
            args)

def TARGET_64(name,*args):
    if _is_64bits():
        TARGET(name,*args)

def TARGET_32(name,*args):
    if not _is_64bits():
        TARGET(name,*args)

def PhonyMode(v):
    tag=SyntaxTag.TagPhonyMode()
    tag.SetV(v)
    return tag

def FileMode(v):
    tag=SyntaxTag.TagFileMode()
    tag.SetV(v)
    return tag

def UseMcy(v):
    tag=SyntaxTag.TagUseMcy()
    tag.SetV(v)
    return tag

def UseUbrpcgen(v):
    tag=SyntaxTag.TagUseUbrpcgen()
    tag.SetV(v)
    return tag

def MCY(v):
    env=Environment.GetCurrent()
    env.SetMcyBinary(v)

def UBRPCGEN(v):
    env=Environment.GetCurrent()
    env.SetUbrpcgenBinary(v)

def PROTOC(v):
    env=Environment.GetCurrent()
    env.SetProtoBinary(v)

def ReplaceExtNameWith(s,orig,new):
    ss=string.split(s)
    ns=[]
    for s in ss:
        (root,ext)=os.path.splitext(s)
        if(ext in (orig,)):
            ns.append('%s%s'%(root,new))
        else:
            ns.append(s)
    return ' '.join(ns)

def GetEnv(key):
    if(key in os.environ):
        return os.environ[key]
    return 'undefined'

def BuildVersion():
    return GetEnv('COMAKE2_BUILD_VERSION')

def Filter(*ss):
    env=Environment.GetCurrent()
    env.LogSystem().LogNotice(
          "syntax 'Filter' is deprecated,use 'Select' instead")
    return Select(*ss) 

def Select(*ss):
    tag=SyntaxTag.TagSelectConfigs()
    tag.AddVs(ss)
    return tag

def Skip(*ss):
    tag=SyntaxTag.TagSkipConfigs()
    tag.AddVs(ss)
    return tag

def ImportConfigsFrom(s,*args):    
    env=Environment.GetCurrent()
    select_configs=[]
    skip_configs=[]
    for arg in args:
        if(isinstance(arg,SyntaxTag.TagSelectConfigs)):
            select_configs.extend(arg.V())
        elif(isinstance(arg,SyntaxTag.TagSkipConfigs)):
            skip_configs.extend(arg.V())
    env.ImportConfigsFrom(s,select_configs,skip_configs)
    
def ConfigsPackage(s):
    env=Environment.GetCurrent()
    (cvspath,codetag,revision,_,_,_)=env.SCMSystem().ParseConfig(s)
    env.CreateConfigsPackage(cvspath,codetag,revision)

def ASH(s):
    env=Environment.GetCurrent()
    env.LogSystem().LogNotice("Detected ASH('%s') in %s"%(s,env.CVSPath()))
    (cvspath,codetag,revision,_,_,_)=env.SCMSystem().ParseConfig(s)
    env.CreateConfigASH(cvspath,codetag,revision)

