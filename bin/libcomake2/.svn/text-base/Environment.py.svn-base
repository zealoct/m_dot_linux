#!/usr/bin/env python
#coding:gbk
#Copyright (c) Baidu.com, Inc. All Rights Reserved 
#author:zhangyan04(@baidu.com)

import os
import platform
import sys
import glob
import json
import time
import signal
import copy
import hashlib
import zlib

import SyntaxTag
import Function
import LogSystem
import BuildSystem
import CodeSystem
import SCMSystem
import Config
import Source
import Target
import ThreadPool
from Syntax import *
import DepAlgorithm

UNBUILT=0
BUILDING=1
BUILDED_OK=2

ENABLE_NEW_DA=True
RECACHE_FLAGS=False

"""
BUG:
1.对于depth=1这个部分的话,可能存在bug.我们必须确定如果多次
ImportConfigsFrom之后的话,模块的depth=1的
"""

class Environment(object):    
    def Print(self,lines):
        lines.append("CC=%s"%(self.Cc()))
        lines.append("CXX=%s"%(self.Cxx()))
        
        cxxflags=self.CxxFlags().V()
        cxxflags_s=self._line_delim.join(cxxflags)
        lines.append("CXXFLAGS=%s"%(cxxflags_s))
        
        cflags=self.CFlags().V()
        cflags_s=self._line_delim.join(cflags)
        lines.append("CFLAGS=%s"%(cflags_s))
        
        cppflags=self.CppFlags().V()
        cppflags_s=self._line_delim.join(cppflags)
        lines.append("CPPFLAGS=%s"%(cppflags_s))
        
        incpaths=self.IncludePaths().V()
        incpaths_s=self._line_delim.join(map(lambda x:"-I%s"%x,incpaths))
        lines.append("INCPATH=%s"%(incpaths_s))

        depends_incpaths=self.DependIncludePaths()
        depends_incpaths_s=self._line_delim.join(
            map(lambda x:"-I%s"%x,
                depends_incpaths))
        lines.append("DEP_INCPATH=%s"%(depends_incpaths_s))

        lines.append("\n#============ CCP vars ============")
        lines.append("CCHECK=%s"%(self.CcheckDriver()))
        lines.append("CCHECK_FLAGS=%s"%(self.CcheckFlags()))
        lines.append("PCLINT=%s"%(self.PclintDriver()))
        lines.append("PCLINT_FLAGS=%s"%(self.PclintFlags()))
        lines.append("CCP=%s"%(self.CcpDriver()))
        lines.append("CCP_FLAGS=%s"%(self.CcpFlags()))
        lines.append("\n")

        md5_content=os.popen('md5sum COMAKE').read().strip()
        lines.append("#COMAKE UUID")
        lines.append("COMAKE_MD5=%s"%md5_content)
        lines.append("\n")

        
    def Clear(self):
        self._workroot=''
        self._cvspath=''
        self._cc='gcc'
        self._cxx='g++'
        self._version=2
        self._copy_using_hard_link=False
        self._mcy_bin=''
        self._ubrpcgen_bin=''
        self._proto_bin=''
        
        self._cflags=SyntaxTag.TagCFlags()
        self._cxxflags=SyntaxTag.TagCxxFlags()
        self._cppflags=SyntaxTag.TagCppFlags()
        self._ldflags=SyntaxTag.TagLinkFlags()
        self._idlflags=SyntaxTag.TagIdlFlags()
        self._ubrpcflags=SyntaxTag.TagUbRpcFlags()
        self._protoflags=SyntaxTag.TagProtoFlags()
        self._incpaths=SyntaxTag.TagIncludePaths()
        self._libs=SyntaxTag.TagLibraries()        
        self._depends_vectors=SyntaxTag.TagLinkLibs()

        self._configs=[]
        self._depends=[]
        self._sources=[]
        self._targets=[]
        self._subdirs=[]
        self._exports=[]

        self._map_configs={}
        self._sorted_configs=[] 
        self._map_configs_deps={} 
        self._map_configs_root={}    
        self._map_depends={}
        self._miss_configs={}
        self._map_configs_package={}

        self._line_delim=' \\\n  '
        self._depends_incpaths=[]

        self._multilibs=False
        self._buildcmd=''

        self._dep_alg_handler=DepAlgorithm.BaiduDepAlgorithm(self)
        self._map_config_args={}
        self._map_config_ashs={}

    def __init__(self):        
        self.Clear()
        self._log_handler=LogSystem.GetCurrent()
        self._scm_handler=SCMSystem.BaiduSCMSystem(self)
        self._bs_handler=BuildSystem.BaiduBuildSystem(self)
        self._cs_handler=CodeSystem.BaiduSVNCodeSystem(self)

        self._doing_update=False
        self._bit=int(platform.architecture()[0][:2])
        self._change_dir='.'
        self._import_files=[]
        self._env_cache={}
        self._env_configs_cache={}
        self._time_compile_link=False
        self._task_threadpool=ThreadPool.ThreadPool()

        self._pclint_driver='@pclint'
        self._pclint_flags=''
        self._ccheck_driver='@ccheck.py'
        self._ccheck_flags=''
        self._ccp_driver='@ccp.py'
        self._ccp_flags=''
        self._ccp_target='ccp'

        self._warn_newer_cfgs=False
        self._scm_audit=0
        self._reference_rev=''

        self._parallel_builds=0
        self._enable_module_cache=False
        self._dump_cfgs=False
        self._diff_configs=''
        self._ccpath = ''
        self._ccversion = ''

    def GetCurrent(self):
        return GetCurrent()
 
    def SetDumpCfgs(self,v):
        self._dump_cfgs=v

    def DumpCfgs(self):
        return self._dump_cfgs

    def SetDiffConfigs(self,v):
        self._diff_configs=v

    def SetNewDA(self,v):
        global ENABLE_NEW_DA
        ENABLE_NEW_DA=v

    def NewDA(self):
        global ENABLE_NEW_DA
        return ENABLE_NEW_DA

    def SetReCache(self,k):
        global RECACHE_FLAGS
        RECACHE_FLAGS=k

    def ReCache(self):
        global RECACHE_FLAGS
        return RECACHE_FLAGS

    def SetParallelBuilds(self,k):
        if(k>=0):
            self._parallel_builds=k
    def EnableParallelBuilds(self):
        return self._parallel_builds>=2
    def SetEnableModuleCache(self, v):
        self._enable_module_cache=v
    def EnableModuleCache(self):
        return self._enable_module_cache
    def LogSystem(self):
        return self._log_handler
    def CodeSystem(self):
        return self._cs_handler
    def BuildSystem(self):
        return self._bs_handler
    def SCMSystem(self):
        return self._scm_handler
    def DepSystem(self):
        return self._dep_alg_handler

    def AppendImportFile(self,v):
        self._import_files.append(v)
    def ImportFiles(self):
        return self._import_files
    def SetDoingUpdate(self,v):
        self._doing_update=v
    def DoingUpdate(self):
        return self._doing_update
    def SetScmAudit(self,v):
        self._scm_audit=v
    def ScmAudit(self):
        return self._scm_audit
    def SetReferenceREV(self,v):
        self._reference_rev=v
    def ReferenceREV(self):
        return self._reference_rev
    def Bit(self):
        return self._bit
    def SetBit(self,bit):
        self._bit=bit
    def CPU(self):
        return os.popen('uname -m').read().strip()
    def ChangeDir(self):
        return self._change_dir
    def SetChangeDir(self,cd):
        self._change_dir=cd
    def TimeCompileLink(self):
        return self._time_compile_link
    def SetTimeCompileLink(self,v):
        #对于编译和链接
        self._time_compile_link=v
    
    def TaskThreadPool(self):
        return self._task_threadpool

    def WorkRoot(self):
        return self._workroot
    def SetWorkRoot(self,k):
        self._workroot=k
    def CVSPath(self):
        return self._cvspath    
    def SetCVSPath(self,k):
        self._cvspath=k
    def Version(self):
        return self._version    
    def SetVersion(self,k):
        self._version=k
    def CopyUsingHardLink(self):
        return self._copy_using_hard_link
    def SetCopyUsingHardLink(self,k):
        self._copy_using_hard_link=k
    def Cc(self):
        return self._cc
    def SetCc(self,k):
        self._cc=k
    def Cxx(self):
        return self._cxx
    def SetCxx(self,k):
        self._cxx=k
    def Multilibs(self):
        return self._multilibs
    def SetMultilibs(self,k):
        self._multilibs=k
    def McyBinary(self):
        return self._mcy_bin
    def SetMcyBinary(self,v):
        self._mcy_bin=v
    def UbrpcgenBinary(self):
        return self._ubrpcgen_bin
    def SetUbrpcgenBinary(self,v):
        self._ubrpcgen_bin=v
    def ProtoBinary(self):
        return self._proto_bin
    def SetProtoBinary(self,v):
        self._proto_bin=v
    def CFlags(self):
        return self._cflags
    def CxxFlags(self):
        return self._cxxflags
    def CppFlags(self):
        return self._cppflags
    def LinkFlags(self):
        return self._ldflags
    def IdlFlags(self):
        return self._idlflags
    def UbRpcFlags(self):
        return self._ubrpcflags
    def ProtoFlags(self):
        return self._protoflags
    def IncludePaths(self):
        return self._incpaths
    def SetDependIncludePaths(self):
        self._depends_incpaths=[]
        for depend in self._depends:
            self._depends_incpaths.extend(
                map(lambda x:os.path.normpath(os.path.join(depend.BasePath(self),x)),
                    depend.IncludePaths()))
        self._depends_incpaths=Function.Unique(self._depends_incpaths)
        self._depends_incpaths.sort(lambda x,y:cmp(x,y))
    def DependIncludePaths(self):
        return self._depends_incpaths
    def Libraries(self):
        return self._libs
    def Configs(self):
        return self._configs
    def Depends(self):
        return self._depends
    def Sources(self):
        return self._sources
    def Targets(self):
        return self._targets
    def PclintDriver(self):
        return self._pclint_driver
    def PclintFlags(self):
        return self._pclint_flags
    def CcheckDriver(self):
        return self._ccheck_driver
    def CcheckFlags(self):
        return self._ccheck_flags
    def CcpDriver(self):
        return self._ccp_driver
    def CcpFlags(self):
        return self._ccp_flags
    def CcpTarget(self):
        return self._ccp_target
    def SetPclintDriver(self,k):
        self._pclint_driver=k
    def SetPclintFlags(self,k):
        self._pclint_flags=k
    def SetCcheckDriver(self,k):
        self._ccheck_driver=k
    def SetCcheckFlags(self,k):
        self._ccheck_flags=k
    def SetCcpDriver(self,k):
        self._ccp_driver=k
    def SetCcpFlags(self,k):
        self._ccp_flags=k
    def SetCcpTarget(self,k):
        self._ccp_target=k
    def SubDirectories(self):
        return self._subdirs
    def SetExports(self,v):
        self._exports=v
    def Exports(self):
        return self._exports
    def SetWarnNewerCfgs(self,v):
        self._warn_newer_cfgs=v
    def _WarnNewerCfgs(self):
        return self._warn_newer_cfgs
    
    def QueryConfig(self,cvspath):
        return self._map_configs[cvspath]
    def QueryCodeTagByCVSPath(self,cvspath):
        config=self._map_configs[cvspath]
        return config.CodeTag()
    def QueryConfigRoot(self,cvspath):
        return self._map_configs_root[cvspath]

    def IsConfigExists(self,cvspath):
        return cvspath in self._map_configs
    def SortedConfigs(self):
        return self._sorted_configs
    def QueryVectorDepsByCVSPath(self,cvspath):        
        return self._map_configs_deps[cvspath][0]
    def QueryDictDepsByCVSPath(self,cvspath):
        return self._map_configs_deps[cvspath][1]
    def AppendConfig(self,cfg):
        if(not cfg.CVSPath() in self._map_configs):
            self._map_configs[cfg.CVSPath()]=cfg
    def AppendSubDirectory(self,v):
        self._subdirs.append(v)
    def IsConfigsPackaged(self,cvspath):
        return cvspath in self._map_configs_package
    def QueryConfigsPackaged(self,cvspath):
        return self._map_configs_package[cvspath]
    def AppendConfigsPackage(self,cfg):
        if(not cfg.CVSPath() in self._map_configs_package):
            self._map_configs_package[cfg.CVSPath()]=cfg
    def AppendConfigArgs(self,cvspath,config_args):
        if(not cvspath in self._map_config_args):
            self._map_config_args[cvspath]=config_args
    def ExistsConfigASH(self,cvspath):
        return cvspath in self._map_config_ashs
    def QueryConfigASH(self,cvspath):
        return self._map_config_ashs[cvspath]
    def AppendConfigASH(self,config_ash):
        if(not config_ash.CVSPath() in self._map_config_ashs):
            self._map_config_ashs[config_ash.CVSPath()]=config_ash

    def IsConfigMissing(self,cvspath,codetag):
        if(not cvspath in self._miss_configs):
            return False
        misscfgs=self._miss_configs[cvspath]
        for cfg in misscfgs:
            if(cfg.CodeTag()==codetag):
                return True
        return False

    def RecordMissConfig(self,cfg,parent=None):
        misscfg=Config.duplicate(cfg,self)
        if(parent):
            misscfg.AppendParent(parent)
        if(not cfg.CVSPath() in self._miss_configs):
            self._miss_configs[cfg.CVSPath()]=[misscfg]
        elif(not self.IsConfigMissing(cfg.CVSPath(),cfg.CodeTag())):
            self._miss_configs[cfg.CVSPath()].append(misscfg)

    def CreateandRecordMissConfig(self,
                             cvspath,
                             codetag,
                             revision,
                             depstag,                     
                             args,buildcmd,status):
        if(not self.IsConfigMissing(cvspath,codetag)):
            misscfg=self._dep_alg_handler.GetOrInitConfigFromArgs(cvspath,
                         codetag,
                         revision,
                         depstag,
                         args,
                         buildcmd,#buildcmd
                         status,#status
                         self)
            if(not cvspath in self._miss_configs):
                self._miss_configs[cvspath]=[misscfg]
            else:
                self._miss_configs[cvspath].append(misscfg)

    def CreateConfigFromArgs(self,
                             cvspath,
                             codetag,
                             revision,
                             depstag,                     
                             args,buildcmd,status):
        """从参数创建Config对象"""
        if(cvspath in self._map_configs):
            self.CreateandRecordMissConfig(cvspath,codetag,revision,depstag,args,buildcmd,status)
            #NOTICE(zhangyan04):
            #需要替换掉args参数.后面args参数更加有效.
            oldcfg=self._map_configs[cvspath]
            newcfg=self._dep_alg_handler.GetOrInitConfigFromArgs(oldcfg.CVSPath(),
                                oldcfg.CodeTag(),
                                oldcfg.Revision(),
                                oldcfg.DepsTag(),
                                args,
                                oldcfg.BuildCmd(),
                                oldcfg.Status(),
                                self)
            self._map_configs[cvspath]=newcfg
            self._map_config_args[cvspath]=args
            return newcfg

        cfg=self._dep_alg_handler.GetOrInitConfigFromArgs(cvspath,
                         codetag,
                         revision,
                         depstag,
                         args,
                         buildcmd,#buildcmd
                         status,#status
                         self)
        self._map_configs[cvspath]=cfg
        self._map_config_args[cvspath]=args
        return cfg

    def CreateConfigASH(self,cvspath,codetag,revision):
        self._map_config_ashs[cvspath]=Config.ConfigASH(cvspath,codetag,revision)

    def CreateDepend(self,
                     cvspath,
                     obj,
                     args):
        """创建Depend对象"""
        s='%s:%s'%(cvspath,obj)
        if(s in self._map_depends):
            return self._map_depends[s]
        dep=Config.Depend(cvspath,obj,args,self)
        self._map_depends[s]=dep
        self._depends.append(dep)
        return dep
    
    def CreateSource(self,name,args):
        """创建Source对象"""
        file_mode=False
        for arg in args:
            if(isinstance(arg,SyntaxTag.TagFileMode)):
                file_mode=True
        #如果强调file模式的话,那么忽略后缀
        #否则根据后缀名来强调规则.
        if(file_mode):
            src=Source.FileSource(name,args,self)
        else:
            (_,ext)=os.path.splitext(name)
            if(ext in Source.IDLSource.EXTS):
                src=Source.IDLSource(name,args,self)
            elif(ext in Source.CSource.EXTS):
                src=Source.CSource(name,args,self)
            elif(ext in Source.CXXSource.EXTS):
                src=Source.CXXSource(name,args,self)
            elif(ext in Source.ProtoSource.EXTS):
                src=Source.ProtoSource(name,args,self)
            else:
                src=Source.FileSource(name,args,self)
        self._sources.append(src)
        return src
    
    def CreateCCPSource(self,name,args):
        """创建CCPSource对象"""
        src=Source.CCPSource(name,args,self)
        self._sources.append(src)
        return src

    def CreateTarget(self,
                     name,
                     type,
                     args):
        """创建Target对象"""
        func_name="[Action:CreateTarget]"
        #很显然需要一些关键字约束
        #REFACTOR(zhangyan04):可能需要更多关键字.
        if(name in ('all',
                    'clean',
                    'love',
                    'dist',
                    #'test',
                    )):
            self._log_handler.LogFatal(
                "%s[keyword:%s]"%(func_name,name))
        #直接根据TARGET类型来创建不同的对象.
        if(type==Target.Application.TYPE):
            target=Target.Application(name,args,self)
        elif(type==Target.StaticLibrary.TYPE):
            target=Target.StaticLibrary(name,args,self)
        elif(type==Target.SharedLibrary.TYPE):
            target=Target.SharedLibrary(name,args,self)
        elif(type==Target.SubDirectory.TYPE):
            target=Target.SubDirectory(name,args,self)
        elif(type==Target.FuzzTarget.TYPE):
            target=Target.FuzzTarget(name,args,self)
        elif(type==Target.NovaTestStub.TYPE):
            target=Target.NovaTestStub(name,args,self)
        elif(type==Target.RUNCCP.TYPE):
            target=Target.RUNCCP(name,args,self)
        self._targets.append(target)
        return target    

    def GetEnvironmentFromCOMAKE(self,s):
        func_name='[Action:GetEnvironmentFromCOMAKE]'
        loc=(os.getcwd(),s)
        f=os.path.join(s,'COMAKE')
        f=os.path.abspath(f)
        #如果COMAKE文件没有存在的话.
        #那么仅仅给出一个Warning警告出来.
        if(not os.path.exists(f)):
            self._log_handler.LogWarning('%s[!exists:%s]'%(
                    func_name,
                    loc))
            #create an empty environment.
            env=Environment()
            return env            
        if(f in self._env_cache):            
            return self._env_cache[f]
        env=Environment()        
        env._map_config_ashs=copy.deepcopy(self._map_config_ashs)
        SetCurrent(env)
        cwd=os.getcwd()
        os.chdir(s)
        execfile('COMAKE')
        os.chdir(cwd)
        SetCurrent(self)
        self._env_cache[f]=env
        return env

    def _NeedReadNextLine(self, line, right_paren_required):
        prev_c = None
        for c in line:
            if c == "#":
                c = prev_c
                break
            if c == "(":
                right_paren_required += 1
            if c == ")":
                right_paren_required -= 1
            prev_c = c

        if c == "\\" or right_paren_required > 0:
            return True, right_paren_required
        else:
            return False, 0

    def _FilterCOMAKEForConfigs(self, f):
        # Cut COMAKE into two parts:
        #   <s>: strings on dep info.
        #   <r>: others.
        s = ''
        r = ''
        next_line = False
        right_paren_required = 0
        fd = open(f, "r")
        lines = fd.readlines()
        fd.close()
        for l in lines:
            orig_line = l
            line = l.strip()
            if not line:
                r += orig_line
                continue
            if next_line:
                # insert '\n' in <r> to maintain line number.
                r += "\n"
                s += line + "\n"
                result, right_paren_required = self._NeedReadNextLine(line, right_paren_required)
                if result:
                    next_line = True
                else:
                    next_line = False
                continue
            if line.startswith("CONFIGS") \
               or line.startswith("WORKROOT") \
               or line.startswith("ImportConfigsFrom") \
               or line.startswith("ConfigsPackage"):
                if line.startswith("WORKROOT"):
                    r += orig_line
                else:
                    r += "\n"
                s += line + "\n" 
                result, right_paren_required = self._NeedReadNextLine(line, 0)
                if result:
                    next_line = True
                continue
            #remaining lines
            r += orig_line
        return (s,r)

    def GetEnvironmentFromCOMAKEForConfigs(self,s,f):
        func_name='[Action:GetEnvironmentFromCOMAKEForConfigs]'
        f=os.path.abspath(f)
        s=os.path.abspath(s)
        #如果COMAKE文件没有存在的话.
        #那么仅仅给出一个Warning警告出来.
        if(not os.path.exists(f)):
            self._log_handler.LogWarning('%s[!exists:%s]'%(
                    func_name,
                    f))
            #create an empty environment.
            env=Environment()
            return env
        if(s in self._env_configs_cache):
            return self._env_configs_cache[s]
        env=Environment()
        env._map_config_ashs=copy.deepcopy(self._map_config_ashs)
        SetCurrent(env)
        cwd=os.getcwd()
        os.chdir(s)
        configstring = self._FilterCOMAKEForConfigs(f)[0]
        exec(configstring)
        os.chdir(cwd)
        SetCurrent(self)
        self._env_configs_cache[s]=env
        return env

    def GetConfigsFromCOMAKE(self,s,f):
        env=self.GetEnvironmentFromCOMAKEForConfigs(s,f)
        return (env._map_configs.values(),env._map_config_args,env._map_config_ashs)

    def InterpretConfigsFromCOMAKE(self,f):
        func_name='[Action:InterpretConfigsFromCOMAKE]'
        if(not os.path.exists(f)):
            self._log_handler.LogFatal('%s[!exists:%s]'%(
                    func_name,
                    f))
        (configstring,otherstring) = self._FilterCOMAKEForConfigs(f)
        exec(configstring)
        return otherstring

    def GetStaticLibraryNamesFromCOMAKE(self,s):
        env=self.GetEnvironmentFromCOMAKE(s)
        return map(lambda x:x.Target(),
                   filter(lambda x:isinstance(x,Target.StaticLibrary),
                          env.Targets()))
    def ImportConfigsFrom(self,s,select_configs=[],skip_configs=[]):
        (configs,config_args,config_ashs)=self.GetConfigsFromCOMAKE(s,os.path.join(s,"COMAKE"))
        if(select_configs):
            configs=map(lambda x:x,
                        filter(lambda x:x.CVSPath() in select_configs,
                               configs))
            for cfg in select_configs:
                found = False
                for cfg2 in configs:
                    if(cfg == cfg2.CVSPath()):
                        found = True
                        break
                if(found == False):
                    self._log_handler.LogWarning('Missing import %s'%cfg)
        if(skip_configs):
            configs=map(lambda x:x,
                        filter(lambda x:not x.CVSPath() in skip_configs,
                               configs))

        cvspath="'%s' @ '%s'"%(os.getcwd(),s)
        for cfg in configs:
            newcfg=self._dep_alg_handler.GetOrInitConfigFromArgs(cfg.CVSPath(),
                                cfg.CodeTag(),
                                cfg.Revision(),
                                cfg.DepsTag(),
                                cfg.Args(),
                                cfg.BuildCmd(),
                                cfg.Status(),
                                self)
            newcfg.AppendImportDir(cvspath)
            self.AppendConfig(newcfg)
            self.AppendConfigArgs(cfg.CVSPath(),config_args[cfg.CVSPath()])
            if(cfg.CVSPath() in config_ashs):
                self.AppendConfigASH(config_ashs[cfg.CVSPath()])

    def ImportConfigsFromSubDirectories(self):
        for subdir in self._subdirs:
            if(os.path.exists(os.path.join(subdir,'COMAKE'))):
                ImportConfigsFrom(subdir)

    def CreateConfigsPackage(self,cvspath,codetag,revision):
        cfg=self.CreateConfigFromArgs(cvspath,codetag,revision,'','','','')
        self._map_configs_root[cvspath]=cvspath
        if(self._doing_update):
            self._cs_handler.Update(cfg)
        configs=self.GetConfigsFromCOMAKE(cfg.BasePath(self), os.path.join(cfg.BasePath(self), "COMAKE"))[0]
        for cfg in configs:
            newcfg=self._dep_alg_handler.GetOrInitConfigFromArgs(cfg.CVSPath(),
                                cfg.CodeTag(),
                                cfg.Revision(),
                                cfg.DepsTag(),
                                cfg.Args(),
                                cfg.BuildCmd(),
                                cfg.Status(),
                                self)
            newcfg.AppendImportDir(cvspath)
            self.AppendConfigsPackage(newcfg)

    def CollectDevDiffs(self):
        self._FillMapConfigsRoot()
        for cvspath in self._map_configs:
            cfg=self._map_configs[cvspath]
            codetag=cfg.CodeTag()
            basepath=cfg.BasePath(self)
            if(self.QueryConfigRoot(cvspath)!=cvspath or
               os.path.abspath(basepath)==os.path.abspath(os.getcwd()) or
               os.path.abspath(basepath).startswith(
                    '%s/'%(os.path.abspath(os.getcwd())))):
                continue
            if((self.SCMSystem().IsTagTrunk(codetag) or \
                self.SCMSystem().IsTagBranch(codetag)) \
                and self.CodeSystem().HasDiffExists(cfg)):
                print '%s'%basepath
             
    def _UniqueDeps(self,deps,mask):
        """编译依赖版本去重 """
        length=len(deps)
        for i in range(0,length):
            cfg_i=deps[i]
            if(mask[i]):
                continue
            for j in range(i+1,length):
                cfg_j=deps[j]
                if(cfg_i==cfg_j):
                    mask[j]=True
                    continue
                if(cfg_i.CVSPath()==cfg_j.CVSPath() \
                    and cfg_i.CodeTag()==cfg_j.CodeTag()):
                    cfg_i.MergeCfg(cfg_j)
                    mask[j]=True
                    continue

    def _DefaultStrategyHandleConflictDeps(self,deps):
        """根据默认策略来处理潜在依赖冲突
        1.如果codetag属于4位tag的话,那么首先选用高版本的
        2.如果codetag属于4位tag并且相同的话,选择指定objects的"""
        new_deps=[]
        length=len(deps)
        mask=[False]*length
        self._UniqueDeps(deps,mask)
        ret=0
        for i in range(0,length):
            if(mask[i]):
                continue
            mask[i]=True
            cfg_i=deps[i]
            collects=[cfg_i]
            for j in range(i+1,length):
                if(mask[j]):
                    continue
                cfg_j=deps[j]
                if(cfg_i.CVSPath()==cfg_j.CVSPath()):
                    mask[j]=True
                    if(cfg_j!=cfg_i):
                        collects.append(cfg_j)
            if(len(collects)<2):
                new_deps.extend(collects)
                continue

            #使用默认策略来完成.
            #1.首先检查是否均为常规4位TAG
            all_4_tag=True
            for cfg in collects:
                if(not self._scm_handler.IsCodeTagTrivial(cfg.CodeTag())):
                    all_4_tag=False
                    break
            if(not all_4_tag):
                new_deps.extend(collects)
                continue

            #2.选择标号最大的内容.
            numbers=map(lambda x:self._scm_handler.Tag2Number(x.CodeTag()),
                        collects)            
            max_number=max(numbers)
            collects=filter(
                lambda x:self._scm_handler.Tag2Number(x.CodeTag())==max_number,
                collects)
            if(len(collects)<2):
                new_deps.extend(collects)
                continue

            #3.选择指定了objects的内容
            tmp_collects=filter(lambda x:x.Objects(),collects)
            if(tmp_collects):
                collects=tmp_collects
            if(len(collects)<2):
                new_deps.extend(collects)
                continue

            #4.没有办法处理冲突了.
            #report conflict.
            ret=-1
            self._log_handler.LogWarning(
                "==========[Conflict:%s]=========="%(cfg_i.CVSPath()))
            for cfg in collects:
                self._log_handler.LogWarning("%s"%(cfg.SerializeToText(0)))
            #new_deps.extend(collects)
        #Over.
        if(ret==-1):        
            sys.exit(-1)
        return new_deps

    def _FillMapConfigsRoot(self):
        #查看模块是否属于另一个模块子模块.
        #如果是这样的话,那么以父模块为准.
        #O(n^2)算法,但是模块数量不会太多,所以时间不是问题.
        self._map_configs_root={}
        cvspaths=self._map_configs.keys()
        cvspaths.sort(lambda x,y:cmp(x,y))
        length=len(cvspaths)
        for i in range(0,length):
            cvspath_i=cvspaths[i]
            self._map_configs_root[cvspath_i]=cvspath_i
        for i in range(0,length):
            cvspath_i=cvspaths[i]
            for j in range(i+1,length):
                cvspath_j=cvspaths[j]
                if(cvspath_j==cvspath_i or
                   cvspath_j.startswith('%s/'%(cvspath_i))):
                    self._map_configs_root[cvspath_j]=cvspath_i
        #需要修改一下CodeTag.
        for i in range(0,length):
            cvspath_i=cvspaths[i]
            cvspath_root=self._map_configs_root[cvspath_i]
            if(cvspath_i==cvspath_root):
                continue
            cfg_i=self._map_configs[cvspath_i]
            cfg_root=self._map_configs[cvspath_root]
            cfg_i.SetCodeTag(cfg_root.CodeTag())
        #Over.
        return

    def _ClosureConfigs(self):
        """求解闭包"""
        #首先下载最上层模块.
        #TODO(zhangyan04):
        #通常来说,迭代的次数不会太多.
        #FillMapConfigsRoot()是O(n^2)的算法.
        #模块最多到100来个,所以耗时不会太多.
        #不用担心这个内容...:).
        #填充父子模块的信息.
        self._FillMapConfigsRoot()

        if(self._cs_handler.EnableParallelUpdates()):
            self._log_handler.SetParallelMode(True)
        if self.DoingUpdate():
            for cfg in self._map_configs.values():
                self._cs_handler.GetRemoteRevision(cfg)
        depth=1

        while(True):            
            deps=[]
            for cfg in self._map_configs.values():
                if(cfg.Depth()==depth and cfg.DisableBuild()==False):
                    deps.append(cfg)
            depth+=1
            extended_list=[]
            for dep in deps:
                subdeps=self._scm_handler.GetCompileDeps(dep.CVSPath(),
                                                         dep.CodeTag(),
                                                         dep.DepsTag(),
                                                         dep.Revision(),
                                                         dep.AtHEAD())
                for subdep in subdeps:
                    #如果上层已经决定的话.
                    if(self.IsConfigExists(subdep.CVSPath())):
                        self.RecordMissConfig(subdep,parent=dep)
                        continue
                    #cfg可能会被共享.所以需要deepcopy.
                    cfg=Config.duplicate(subdep,self)
                    cfg.AppendParent(dep)
                    extended_list.append(cfg)
            #使用默认策略来处理冲突.
            extended_list=self._DefaultStrategyHandleConflictDeps(extended_list)
            #把扩展的模块加入其中.
            for ext in extended_list:
                if self.DoingUpdate():
                    self._cs_handler.GetRemoteRevision(ext)
                self.AppendConfig(ext)
            #填充父子模块的信息.
            self._FillMapConfigsRoot()
            if(not extended_list):
                break
        #写到_configs下面.
        self._configs=self._map_configs.values()
        if(self._cs_handler.WaitOtherUpdatesFinish()!=0):
            sys.exit(1)
        self._log_handler.SetParallelMode(False)
        return

    def _parallel_sig_handler(self, sig, stack): 
        signal.signal (sig, signal.SIG_IGN)
        msg='Paralleling process being killed cause some process ended in failure'
        self._log_handler.LogWarning(msg)
        signal.signal (sig, signal.SIG_DFL)
        os.kill(int(os.getpid()), sig)

    def set_signal_handler(self):
        signal.signal(signal.SIGTERM, self._parallel_sig_handler)
        signal.signal(signal.SIGHUP, self._parallel_sig_handler)
        signal.signal(signal.SIGINT, self._parallel_sig_handler)

    def _CompareReleases(self,oldtag,newtag):
        number1=self._scm_handler.Tag2Number(oldtag)
        number2=self._scm_handler.Tag2Number(newtag)
        max_number=max(number1,number2)
        return max_number != number1 

    def _FindNewerCfg(self,oldcfg,newcfg):
        result=self._scm_handler.CompareConfigs(oldcfg,newcfg)
        if(self._scm_handler.IsNewer(result)):
            return False
        elif(self._scm_handler.MissNewer(result)):
            return True
        else:
            #both are developing. warn it!
            self._log_handler.LogWarning(
                "==========[Conflict:%s]=========="%(oldcfg.CVSPath()))
            self._log_handler.LogWarning("%s"%(oldcfg.SerializeToText(0)))
            self._log_handler.LogWarning("%s"%(newcfg.SerializeToText(0)))
 
    def _DoWarnNewerCfg(self,oldcfg,newcfg):
        if((self._WarnNewerCfgs()==True or self.ScmAudit())
            and self._FindNewerCfg(oldcfg,newcfg)): 
            msg="可能需要更新的依赖:[cvspath:%s][local:%s][newer:%s]"%(oldcfg.CVSPath(),
                                                                   oldcfg.CodeTag(),
                                                                   newcfg.CodeTag())
            self._log_handler.LogWarning(msg)
            print "local:\n%s"%(oldcfg.SerializeToText(0,forshort=True))
            print "newer:\n%s"%(newcfg.SerializeToText(0,forshort=True))

    def _WarnMissNewerConfigs(self):
        for cvspath in self._miss_configs:
            ex_cfg=self.QueryConfig(cvspath)
            for cfg in self._miss_configs[cvspath]: 
                self._DoWarnNewerCfg(ex_cfg,cfg)

    def _FillMapConfigsDeps(self):
        #建立正向依赖.
        #这里我们可能需要调用GetCompileDeps多次.
        top_list=list()
        for cfg in self._configs:
            flags={}
            changed=True
            res_deps=[]
            while(changed):
                changed=False
                if(cfg.DisableBuild()==False):
                    deps=self._scm_handler.GetCompileDeps(cfg.CVSPath(),
                                                      cfg.CodeTag(),
                                                      cfg.DepsTag(),
                                                      cfg.Revision(),
                                                      cfg.AtHEAD())
                else:
                    deps=[]
                for dep in deps:
                    if(dep.CVSPath() in flags):
                        continue
                    changed=True
                    flags[dep.CVSPath()]=True
                    res_deps.append(dep.CVSPath())
                #按照字母顺序进行排序.:).
                res_deps.sort(lambda x,y:cmp(x,y))
                #里面对应使用了数组和字典两种结构
                self._map_configs_deps[cfg.CVSPath()]=(res_deps,flags)

    def _merge_into_graph(self,cvspath,gnode):
        for gn in gnode:
            if(cvspath in self.QueryVectorDepsByCVSPath(gn) \
                or gn in self.QueryVectorDepsByCVSPath(cvspath)):
                return False
        gnode.append(cvspath)
        return True

    def GraphGrouping(self):
        graph_info=list()
        for i in range(len(self._sorted_configs)):
            cvspath=self._sorted_configs[i].CVSPath()
            merged_flag=False
            for g in graph_info:
                merged_flag=self._merge_into_graph(cvspath,g)
                if(merged_flag==True):
                    break
            if(merged_flag==False):
                graph_info.append([cvspath])
        self._log_handler.LogDebug('======================')
        self._log_handler.LogDebug('=== Graph Grouping ===')
        self._log_handler.LogDebug('======================')
        self._log_handler.LogDebug('Tips: deps in the same level do not depend each other')
        for i in range(len(graph_info)):
            self._log_handler.LogDebug('Level %d, number %d:%s'%(i+1, \
                                       len(graph_info[i]), \
                                       json.dumps(graph_info[i],sort_keys=True, indent=4)))
                                
    def _SortConfigs(self):
        """按照top顺序排序"""
        self._sorted_configs=[]
        flag_configs={}
        def _SortConfigsRecursive(cfg):
            if(cfg.CVSPath() in flag_configs):
                return
            if(cfg.DisableBuild()==False):
                deps=self._scm_handler.GetCompileDeps(cfg.CVSPath(),
                                                  cfg.CodeTag(),
                                                  cfg.DepsTag(),
                                                  cfg.Revision(),
                                                  cfg.AtHEAD())
            else:
                deps=[]
            for dep in deps:
                subcfg=self.QueryConfig(dep.CVSPath())
                _SortConfigsRecursive(subcfg)
            flag_configs[cfg.CVSPath()]=True
            self._sorted_configs.append(cfg)
            return
        for cfg in self._configs:
            _SortConfigsRecursive(cfg)
        self.GraphGrouping()
        return
        
    def DumpConfigs(self):
        contents_scm = []
        print "#cvspath,trunk/branches,localrev,localtag,cleancmd,makecmd"
        print ""
        (cleancmd,makecmd)=('make clean','make')
        cvspath=self._cvspath
        (localtag,localrev)=self._cs_handler.GetTagAndRevision(cvspath,query_config_root=False)
        if(self._scm_handler.IsTagTrunk(localtag)):
            print "%s,trunk,%s,,%s,%s"%(cvspath,localrev,cleancmd,makecmd)
        elif(self._scm_handler.IsTagBranch(localtag)):
            print "%s,%s,%s,,%s,%s"%(cvspath,localtag,localrev,cleancmd,makecmd)
        else:
            print "%s,,%s,%s,%s,%s"%(cvspath,localrev,localtag,cleancmd,makecmd)
        TAB_WIDTH=' '*4
        flag_configs={}
        for cfg in self._sorted_configs:
            cvspath=cfg.CVSPath()
            #NOTICE(zhangyan04)如果这个属于其他模块子目录的话.那么也不会发生更新.
            #或者是当前目录的子目录,是不会发生更新的.
            #p.s.:下载机制和更新机制类似
            if(cvspath==self._cvspath
               or cvspath.startswith('%s/'%self._cvspath)):
                continue
            if(self.QueryConfigRoot(cvspath)!=cvspath):
                continue
            codetag = cfg.CodeTag()
            revision = cfg.Revision()
            if(not cfg.DisableBuild()):
                (cleancmd,makecmd)=self._bs_handler.GetCommands(cfg,for_scm=True)
            else:
                (cleancmd,makecmd)=('','')
            print TAB_WIDTH,
            if(self._scm_handler.IsTagTrunk(codetag)):
                print "%s,trunk,%s,,%s,%s"%(cvspath,revision,cleancmd,makecmd)
            elif(self._scm_handler.IsTagBranch(codetag)):
                print "%s,%s,%s,,%s,%s"%(cvspath,codetag,revision,cleancmd,makecmd)
            else:
                print "%s,,%s,%s,%s,%s"%(cvspath,revision,codetag,cleancmd,makecmd)
                continue

            def _ExportLocalSubConfigs(_cvspath,flag_configs,contents_scm,level):
                deps=self.QueryVectorDepsByCVSPath(_cvspath)
                for dep in deps:
                    cfg=self.QueryConfig(dep)
                    cvspath=cfg.CVSPath()
                    flag_configs[cvspath]=True
                    codetag = cfg.CodeTag()
                    revision = cfg.Revision()
                    if(not cfg.DisableBuild()):
                        (cleancmd,makecmd)=self._bs_handler.GetCommands(cfg,for_scm=True)
                    else:
                        (cleancmd,makecmd)=('','')
                    print TAB_WIDTH*level,
                    if(self._scm_handler.IsTagTrunk(codetag)):
                        print "%s,trunk,%s,,%s,%s"%(cvspath,revision,cleancmd,makecmd)
                    elif(self._scm_handler.IsTagBranch(codetag)):
                        print "%s,%s,%s,,%s,%s"%(cvspath,codetag,revision,cleancmd,makecmd)
                    else:
                        print "%s,,%s,%s,%s,%s"%(cvspath,revision,codetag,cleancmd,makecmd)
                        continue

                    if(cvspath in flag_configs):
                        continue
                    _ExportLocalSubConfigs(cvspath,flag_configs,contents_scm,level+1)

            _ExportLocalSubConfigs(cvspath,flag_configs,contents_scm,2)
            flag_configs[cvspath]=True

    def _CreateConfigforMain(self):
        (localtag,localrev)=self._cs_handler.GetTagAndRevision(self._cvspath,query_config_root=False)
        cfg=self._dep_alg_handler.GetOrInitConfigFromArgs(self._cvspath,
                         localtag,
                         localrev,
                         'comake',
                         [],#args
                         '',#buildcmd
                         '',#status
                         self)
        key=self._scm_handler.GetDepKey(cfg.CVSPath(),
                                        cfg.CodeTag(),
                                        cfg.DepsTag(),
                                        cfg.Revision(),
                                        cfg.AtHEAD())
        if(self._cvspath in self._map_configs):
            self._log_handler.LogWarning('Found %s circle-depending, ignored'%self._cvspath)
            del self._map_configs[self._cvspath]
            del self._map_config_args[self._cvspath]
        self._scm_handler.SetCompileDepsCache(key,self._map_configs.values())
        self._scm_handler.SetCompileArgsCache(key,self._map_config_args)
        return cfg
 
    def ActionConfigs(self):
        """执行Configs"""
        #1.获得Configs闭包
        #2.对Configs依赖进行排序
        #3.对Configs检测所依赖的Depends
        func_name="[Action:ActionConfigs]"
        if(self.NewDA()==True):
            main_module=self._CreateConfigforMain()
            self._dep_alg_handler.DepAlgorithm(main_module)
        else:
            self._ClosureConfigs()
            self._WarnMissNewerConfigs()
            self._FillMapConfigsDeps()
            self._SortConfigs()
        if(self._diff_configs):
            self._DiffConfigs()
            return
        if(self._dump_cfgs):
            self.DumpConfigs()
            return

        if self._doing_update:
            if(self._cs_handler.EnableParallelUpdates()):
                self._log_handler.SetParallelMode(True)
                self._cs_handler.ResetUpdates()
            for cfg in self._configs:
                self._cs_handler.Update(cfg)
            if(self._cs_handler.WaitOtherUpdatesFinish()!=0):
                sys.exit(1)
            self._log_handler.SetParallelMode(False)
        delim='\n'
        self._log_handler.LogDebug("%s[configs:%s]"%(
                func_name,delim.join(map(lambda x:str(x),
                                         self._sorted_configs))))
        if(self._scm_audit==0):
            return
        print "============================="
        print "=== 调序和打平 - 自动进行 ==="
        print "============================="
        self.WatchConfigs(0)
        print "=============================="
        print "=== 对比平台维护的依赖列表 ==="
        print "=============================="
        configs = self._sorted_configs
        configs='\n'.join(map(lambda x:"CONFIGS('%s@%s')"%(x.CVSPath(),
                                                               x.CodeTag()),configs))
        open('COMAKE.CONFIGS.0','w').write(configs+'\n')
        if(self.ReferenceREV()):
            self.ExportConfigs('%s@%s@%s'%(self.CVSPath(),
                                           self.ReferenceREV(),
                                           self.ReferenceREV()))
            rev=self.ReferenceREV()
        else:
            self.ExportConfigs(self.CVSPath())
            rev="最新基线"
        if(os.system('diff -ur COMAKE.CONFIGS COMAKE.CONFIGS.0') == 0):
            print "和SCMPF平台记录的%s的依赖列表无diff"%rev
        else:
            print "%s"%Function.RedIt('请自行检查和SCMPF平台记录的%s的依赖列表存在的diff！'%rev)
        print "================"
        print "=== 版本审计 ==="
        print "================"
        for cfg in self._sorted_configs:
            (cvspath,codetag,status)=(cfg.CVSPath(),cfg.CodeTag(),cfg.Status())
            if(status == "released"
               or status == "pre-release"
               or status == "buildreleased"
               or status == "releasing"):
                print "[cvspath:%s][local:%s][status:%s]"%(cvspath,
                                                           codetag,
                                                           Function.GreenIt(status))
            elif(status == ""):
                print "[cvspath:%s][local:%s][status:%s]"%(cvspath,
                                                           codetag,
                                                           Function.RedIt("Undefined"))
            else:
                print "[cvspath:%s][local:%s][status:%s]"%(cvspath,
                                                           codetag,
                                                           Function.RedIt(status))
        if(self._scm_audit==1):
            return
        print "=============================="
        print "=== 对比最新基线，自动推送 ==="
        print "=============================="
        for cfg in self._sorted_configs:
            (cvspath,codetag)=(cfg.CVSPath(),cfg.CodeTag())
            latest_tag=self._scm_handler._GetFormalTag(cvspath,'')
            if(codetag != latest_tag):
                print "[cvspath:%s][local:%s][HEAD:%s]"%(cvspath,codetag,
                                                           Function.RedIt(latest_tag))
            else:
                print "[cvspath:%s][local:%s][%s]"%(cvspath,codetag,
                                                           Function.GreenIt('latest'))

    def ActionDepends(self):
        """执行Depends"""
        func_name="[Action:ActionDepends]"
        #因为我们最终依赖的不是configs而是很多Depend对象.
        #所以我们必须得到每个config所持有的depend对象.
        #这样一旦我们依赖某个config,隐含地我们其实依赖的是
        #config所持有的depend对象 
        for cfg in self._configs:
            cfg.CreateDepends(self)
        for depend in self._depends:
            depend.Detect()
        self._log_handler.LogDebug("%s[depends:%s]"%(
                func_name,
                '\n'.join(map(lambda x:'%s:%s'%(x.CVSPath(),
                                                x.Object()),
                              self._depends))))
    
    def NeedBuilded(self,cfg,builded_set):
        deps=self.QueryVectorDepsByCVSPath(cfg.CVSPath())
        needed=False
        for dep in deps:
            if(dep in builded_set):
                needed=True
                break
        needed = (needed or self._bs_handler.NeedBuilded(cfg))
        
        if not needed and self.IsCached(cfg):
            builded_set.add(cfg.CVSPath())
        return needed

    def BuildConfigs(self):
        """构建编译环境"""
        self._bs_handler.init_cc_info()

        if(self.EnableParallelBuilds()):
            self.BuildinParallel()
            self.ClearAllCachedTag()
            return
        
        func_name='[Action:BuildConfigs]'
        if(Function.PYTHON_HIGH_VERSION):            
            builded_set=set()
        else:
            import sets
            builded_set=sets.Set()
        for cfg in self._sorted_configs:
            if(not self.NeedBuilded(cfg,builded_set)):
                self._log_handler.LogNotice(
                    '%s[builded:%s]'%(func_name,cfg.CVSPath()))
                continue
            self._bs_handler.Build(cfg)
            builded_set.add(cfg.CVSPath())                    
        self.ClearAllCachedTag()

    def BuildinParallel(self):
        func_name='[Action:BuildinParallel]'
        if(Function.PYTHON_HIGH_VERSION):            
            #nbb_set: newly builded and building set
            nbb_set=set()
            building_set=set()
        else:
            import sets
            nbb_set=sets.Set()
            building_set=sets.Set()

        build_status_info=dict()
        for cfg in self._sorted_configs:
            self._SetBuildStatusInfo(build_status_info,cfg.CVSPath(),[None,UNBUILT])

        self._log_handler.SetParallelMode(True)
        while(True):
            builded_ok_no=0
            builded_set_len=len(nbb_set)
            for cfg in self._sorted_configs:
                cvspath=cfg.CVSPath()
                if(self._QueryBuildStatusByCVSPath(build_status_info,cvspath)==BUILDED_OK):
                    builded_ok_no+=1
                    continue
                elif(self._QueryBuildStatusByCVSPath(build_status_info,cvspath)==BUILDING):
                    if(self._PromoteBuildStatus(cvspath,building_set,build_status_info)):
                        builded_ok_no+=1
                    continue 
                if(not self.NeedBuilded(cfg,nbb_set)):
                    self._SetBuildStatusInfo(build_status_info,cvspath,[None,BUILDED_OK])
                    builded_ok_no+=1
                    #already builded, exluded from nbb_set
                    self._log_handler.LogNotice(
                        '%s[builded:%s]'%(func_name,cvspath))
                    continue
                deps=self.QueryVectorDepsByCVSPath(cvspath)
                if(deps==list()):
                    if(self._AddNewBuilding(cfg,building_set,nbb_set,build_status_info)==False):
                        break
                    continue
                ready=True
                for dep in deps:
                    if(self._QueryBuildStatusByCVSPath(build_status_info,dep)!=BUILDED_OK):
                        ready=False
                        break
                if(ready==False):
                    continue
                if(self._AddNewBuilding(cfg,building_set,nbb_set,build_status_info)==False):
                    break
            #done when all deps are builded ok
            if(builded_ok_no>=len(self._sorted_configs)):
                break
            #take relax if no new building modules add in ...
            if(builded_set_len==len(nbb_set)):
                time.sleep(1)
        self._log_handler.SetParallelMode(False)
        return

    def _AddNewBuilding(self,cfg,building_set,nbb_set,build_status_info):
        cvspath=cfg.CVSPath()
        tmp_building_set=copy.copy(building_set)
        for s in tmp_building_set:
            self._PromoteBuildStatus(s,building_set,build_status_info)
        #stop forking if reaching limitation, re-scan from first to see if some buildings ended.
        if(len(building_set)>=self._parallel_builds):
            return False
        pid=self._bs_handler.BuildonFork(cfg)
        if(pid==-1):
            self._SetBuildStatusInfo(build_status_info,cvspath,[None,BUILDED_OK])
        else:
            self._SetBuildStatusInfo(build_status_info,cvspath,[pid,BUILDING])
            building_set.add(cvspath)
        nbb_set.add(cvspath)
        return True
    def _PromoteBuildStatus(self,cvspath,building_set,build_status_info):
        pid=self._QueryBuildPidByCVSPath(build_status_info,cvspath)
        wpid, status = os.waitpid(pid, os.WNOHANG)
        if wpid > 0:
            building_set.remove(cvspath)
            if status!=0:
                self._WaitOtherBuildingsFinish(cvspath,building_set,build_status_info)
                sys.exit(1)
            else:
                self._SetBuildStatusInfo(build_status_info,cvspath,[None,BUILDED_OK])
                return True
        return False
    def _WaitOtherBuildingsFinish(self,cvspath,building_set,build_status_info):
        result=0
        for cvspath in building_set:
            pid=self._QueryBuildPidByCVSPath(build_status_info,cvspath)
            wpid, status = os.waitpid(pid, 0)
            if status!=0:
                result=1
        return result
    def _QueryBuildPidByCVSPath(self,build_status_info,cvspath):
        return build_status_info[cvspath][0]
    def _QueryBuildStatusByCVSPath(self,build_status_info,cvspath):
        return build_status_info[cvspath][1]
    def _SetBuildStatusInfo(self,build_status_info,cvspath,st_info):
        build_status_info[cvspath]=st_info

    def _BuildCmdString(self, cfg):
        buildcmd = cfg.BuildCmd()
        func_name = "[BuildCmdString]"
        if not self._ccpath:
            command='which gcc'
            (status,output,err)=self._log_handler.LogDebugWithCC(
                '%s[cmd:%s]'%(func_name,command),
                command,
                2)
            if status:
                self._log_handler.LogWarning('can not get gcc path')
                return ''
            else:
                output=output.strip()
            self._ccpath = output
        buildcmd += "@" + self._ccpath

        if not self._ccversion:
            command='gcc -dumpversion'
            (status,output,err)=self._log_handler.LogDebugWithCC(
                '%s[cmd:%s]'%(func_name,command),
                command,
                2)
            if status:
                self._log_handler.LogWarning('can not get gcc version')
                return ''
            else:
                output=output.strip()
            self._ccversion = output
        buildcmd += "@gcc-" + self._ccversion
        return buildcmd

    def _ModuleString(self, cfg):
        cvspath = cfg.CVSPath()
        codetag = cfg.CodeTag()
        revision = cfg.Revision()
        if not self.DoingUpdate() and not revision:
            localtag, localrev = self._cs_handler.GetTagAndRevision(cvspath,query_config_root=False)
            cfg._revision = localrev
            revision = localrev
        buildcmd = self._BuildCmdString(cfg)
        if not buildcmd:
            return ''
        return "--module=%s,%s,%s,%s"%(cvspath, codetag, revision, buildcmd)

    def _DepString(self, cfg):
        depstring = '--deps='
        deps = self.QueryVectorDepsByCVSPath(cfg.CVSPath())
        depinfo_list = list()
        for dep in deps:
            dep_cfg = self.QueryConfig(dep)
            codetag = dep_cfg.CodeTag()
            revision = dep_cfg.Revision()
            if not self.DoingUpdate() and not revision:
                localtag, localrev = self._cs_handler.GetTagAndRevision(dep,query_config_root=False)
                dep_cfg._revision = localrev
                revision = localrev
            buildcmd = self._BuildCmdString(dep_cfg)
            if not buildcmd:
                return ''
            depinfo_list.append("%s,%s,%s,%s"%(dep, codetag, revision, buildcmd))
        if len(depinfo_list) > 0:
            depinfo_list.sort()
            depstring += ":".join(depinfo_list)
        return depstring 
   
    def _RunMcache(self, cmd, modulestring, depstring):
        pid = os.fork()
        if pid > 0:
            wpid, status = os.waitpid(pid, 0)
            return status
        elif pid == 0:
            os.chdir(self.WorkRoot())
            cmdlist = list()
            cmdlist.append("mcache")
            cmdlist.append(cmd)
            cmdlist.append(modulestring)
            cmdlist.append(depstring)
            os.execvp("mcache", cmdlist)
            os._exit(-1)
        else:
            return -1
    
    def MarkCached(self, cfg, modulestring, depstring):
        cachedtag = os.path.join(cfg.BasePath(self), ".CACHED_TAG")
        f = open(cachedtag, "w")
        f.write(modulestring)
        f.write("\n")
        f.write(depstring)
        f.close()
        return  

    def IsCached(self, cfg, modulestring = None, depstring = None):
        cachedtag = os.path.join(cfg.BasePath(self), ".CACHED_TAG")
        if not os.path.exists(cachedtag):
            return False
        if modulestring:
            f = open(cachedtag, "r")
            cacheinfo = f.read()
            f.close()
            return cacheinfo == "%s\n%s"%(modulestring, depstring)
        else:
            return True

    def ClearCachedTag(self, cfg):
        cachedtag = os.path.join(cfg.BasePath(self), ".CACHED_TAG")
        if os.path.exists(cachedtag):
            os.remove(cachedtag)

    def ClearAllCachedTag(self):
        for cfg in self._sorted_configs:
            cachedtag = os.path.join(cfg.BasePath(self), ".CACHED_TAG")
            if os.path.exists(cachedtag):
                os.remove(cachedtag)

    def CacheHit(self, cfg):
        if not self.EnableModuleCache():
            return False
        if self._cs_handler._no_revert:
            return False
        func_name = "[Action:CacheHit][cvspath:%s]"%cfg.CVSPath()
        modulestring = self._ModuleString(cfg)
        if not modulestring:
            return False
        depstring = self._DepString(cfg)
        if not depstring:
            return False
        # Already cache hit
        if self.IsCached(cfg, modulestring, depstring):
            self._log_handler.LogNotice("%s[AlreadyHit]"%func_name)
            return True
        if self._RunMcache("--from", modulestring, depstring) != 0:
            return False
        self._log_handler.LogNotice(func_name)
        self.MarkCached(cfg, modulestring, depstring)
        return True

    def CodeModified(self, cfg):
        if self._bs_handler.IsModified(cfg):
            return True
        deps = self.QueryVectorDepsByCVSPath(cfg.CVSPath())
        for dep in deps:
            if(not dep in self._map_configs):
                continue
            dep_cfg = self.QueryConfig(dep)
            if self._bs_handler.IsModified(dep_cfg):
                return True
        return False

    def ToCache(self, cfg):
        if not self.EnableModuleCache():
            return 
        if self.CodeModified(cfg):
            return 
        modulestring = self._ModuleString(cfg)
        if not modulestring:
            return 
        depstring = self._DepString(cfg)
        if not depstring:
            return
        if self._RunMcache("--to", modulestring, depstring) != 0:
            return
        func_name = "[Action:ToCache][cvspath:%s]"%cfg.CVSPath()
        self._log_handler.LogNotice(func_name)
        return 

    def LinkLibs(self):
        if(self._depends_vectors.V()!=list()):
            return self._depends_vectors
        depends=filter(lambda x:x.Object()!=os.path.normpath(''),
                             self._depends)
        depends_libs=list()
        for depend in depends:
            depends_libs.append(os.path.join(depend.BasePath(self),
                                                   depend.Object()))
        depends_libs.sort(lambda x,y:cmp(x,y))
        total_libs=self._libs.V()+depends_libs
        for lib in total_libs:
            self._depends_vectors.AddV(lib)
        return self._depends_vectors
    
    def Action(self):
        #之前需要进行
        #1.ActionConfigs
        #2.ActionDepends
        func_name="[Action:Action]"        
        #NOTICE(zhangyan04):需要检查所有模块是否存在.3ks yufan.
        #这样确实能够让用户尽早发现模块确实问题.
        for cfg in self._sorted_configs:
            basepath=os.path.join(self.WorkRoot(),cfg.CVSPath())
            if(not os.path.exists(basepath)):
                self._log_handler.LogFatal(
                    '%s[cvspath:%s][status:!exists]'%(
                        func_name,cfg.CVSPath()))
        if(not self._mcy_bin):
            self._mcy_bin='%s/public/idlcompiler/output/bin/mcy'%(self._workroot)
        if(not self._ubrpcgen_bin):
            self._ubrpcgen_bin='%s/public/idlcompiler/output/bin/ubrpcgen'%(self._workroot) 
        if(not self._proto_bin):
            self._proto_bin='%s/thirdsrc/protobuf/install/bin/protoc'%(self._workroot) 

        #Set include paths of all depends.
        self.SetDependIncludePaths()

        for target in self._targets:
            target.Action()

        #如果没有制定epxorts的话
        #那么使用target的内容能够.
        #RUNCCP target should not be exported in any targets except 'ccp'.
        if(not self._exports):
            self._exports=map(lambda x:x.Target(),
                              filter(lambda x:not isinstance(x,Target.RUNCCP),
                                     self._targets))
        return

    def GenConfigsForCOMAKE(self,
                            cvspath,
                            codetag,
                            depstag):
        func_name="[Action:GenConfigsForCOMAKE]"
        configs=''
        cfg_list=[]
        try:
            deps=self._scm_handler.GetCompileDeps(cvspath,
                                                  codetag,
                                                  depstag)
            deps.sort(lambda x,y:cmp(x.CVSPath(),
                                     y.CVSPath()))
            deps=Function.Unique(deps,lambda x:x.CVSPath())
            for d in deps:
                if(d.CodeTag()==d.DepsTag()):
                    cfg_list.append("CONFIGS('%s@%s')"%(d.CVSPath(),d.CodeTag()))
                else:
                    cfg_list.append("CONFIGS('%s@%s@%s')"%(d.CVSPath(),d.CodeTag(),d.DepsTag()))
            configs='\n'.join(cfg_list)
        except Exception,e:
            self._log_handler.LogNotice(
                "%s[GetCompileDeps:failed][cvspath:%s][Exception:%s]"%(
                    func_name,cvspath,e))
        if(not self._cvspath):
            self._cvspath=cvspath
        return configs

    def ExportConfigs(self,v):
        """导出编译依赖"""
        func_name='[Action:ExportConfigs]'
        (cvspath,
         codetag,
         revision,
         depstag,_,_)=self._scm_handler.ParseConfig(v)
        configs=self.GenConfigsForCOMAKE(cvspath,codetag,depstag)
        comake_file='COMAKE.CONFIGS'
        open(comake_file,'w').write(configs+'\n')
        self._log_handler.LogNotice("%s[exported configs to %s]"%(func_name,comake_file))

    def _GetBaseConfigs(self,v):
        func_name="[Action:_GetBaseConfigs]"
        if(not v.__contains__('@')):
            v='%s@%s'%(self.CVSPath(),v)
        (cvspath,
         codetag,
         revision,
         depstag,_,_)=self._scm_handler.ParseConfig(v)
        if(self._scm_handler.IsTagNull(codetag)):
            self._log_handler.LogFatal('Invalid module path or version, please check it!')
        cfg_list=list()
        try:
            deps=self._scm_handler.GetCompileDeps(cvspath,
                                                  codetag,
                                                  depstag)
            deps.sort(lambda x,y:cmp(x.CVSPath(),
                                     y.CVSPath()))
            deps=Function.Unique(deps,lambda x:x.CVSPath())
            for d in deps:
                cfg_list.append("%s@%s"%(d.CVSPath(),d.CodeTag()))
        except Exception,e:
            self._log_handler.LogFatal(
                "%s[GetCompileDeps:failed][cvspath:%s][Exception:%s]"%(
                    func_name,cvspath,e))
        base_file=".%s-%s"%(cvspath.replace('/','_'),depstag)
        open(base_file,'w').write('\n'.join(cfg_list)+'\n')
        return base_file

    def _DiffConfigs(self):
        func_name="[Action:_DiffConfigs]"
        base_file=self._GetBaseConfigs(self._diff_configs)
        deps=self._sorted_configs
        deps.sort(lambda x,y:cmp(x.CVSPath(),
                                     y.CVSPath()))
        cfg_list=list()
        for d in deps:
            cfg_list.append("%s@%s"%(d.CVSPath(),d.CodeTag()))
        local_file=".%s-local"%(self.CVSPath().replace('/','_'))
        open(local_file,'w').write('\n'.join(cfg_list)+'\n')
        command='diff -ur %s %s'%(base_file,local_file)
        (status,output,err)=self._log_handler.LogNoticeWithCC(
                '%s[cmd:%s]'%(func_name,command),
                command)
        if(output):
            print output, 
        if(status!=0):
            sys.exit(1)

    def _GenerateConfigLine(self,cvspath,cfg):
        istag=False
        if(cfg):
            (localtag,localrev)=self._cs_handler.GetTagAndRevision(cvspath,query_config_root=False)
            (cleancmd,makecmd)=self._bs_handler.GetCommands(cfg,for_scm=True)
            if(self._scm_handler.IsTagTrunk(localtag)):
                scm_line="%s,trunk,%s,,%s,%s"%(cvspath,localrev,cleancmd,makecmd)
            elif(self._scm_handler.IsTagBranch(localtag)):
                scm_line="%s,%s,%s,,%s,%s"%(cvspath,localtag,localrev,cleancmd,makecmd)
            else:
                scm_line="%s,,%s,%s,%s,%s"%(cvspath,localrev,localtag,cleancmd,makecmd)
                istag=True
            if(istag==False \
                and cfg.StableRevision()==False):
                unstable_revision_flag='unstable'
            else:
                unstable_revision_flag=''
            if(cfg.DisableBuild()):
                disable_build_flag='disbuild'
            else:
                disable_build_flag=''
            scm_line=scm_line+',%s,DEP-%s,%s'%(disable_build_flag,cfg.Depth(),unstable_revision_flag)
        else:
            (cleancmd,makecmd)=('make clean','make')
            (localtag,localrev)=self._cs_handler.GetTagAndRevision(cvspath,query_config_root=False)
            if(self._scm_handler.IsTagTrunk(localtag)):
                scm_line="%s,trunk,%s,,%s,%s"%(cvspath,localrev,cleancmd,makecmd)
            elif(self._scm_handler.IsTagBranch(localtag)):
                scm_line="%s,%s,%s,,%s,%s"%(cvspath,localtag,localrev,cleancmd,makecmd)
            else:
                scm_line="%s,,%s,%s,%s,%s"%(cvspath,localrev,localtag,cleancmd,makecmd)
                istag=True
        return (scm_line,istag)
 
    def ExportLocalConfigs(self):
        """导出本地环境"""
        func_name='[Action:ExportLocalConfigs]'
        contents_scm=[]
        contents_scm.append("### COMAKE2: PLEASE DO NOT DELETE THE FILE\n")
        contents_scm.append("#<cvspath>,trunk/<branch-name>/-,<localrev>,<tag-name>/-,<cleancmd>,<makecmd>,disbuild/-,DEP-<N>,unstable/-\n")

        contents_scm.append(self._GenerateConfigLine(self._cvspath,None)[0]+'\n')

        TAB_WIDTH=' '*4
        flag_configs={}
        
        for cfg in self._sorted_configs:
            cvspath=cfg.CVSPath()
            #NOTICE(zhangyan04)如果这个属于其他模块子目录的话.那么也不会发生更新.
            #或者是当前目录的子目录,是不会发生更新的.
            #p.s.:下载机制和更新机制类似
            if(cvspath==self._cvspath 
               or cvspath.startswith('%s/'%self._cvspath)):
                continue
            if(self.QueryConfigRoot(cvspath)!=cvspath):
                continue
            contents_scm.append(TAB_WIDTH)
            (scm_line,istag)=self._GenerateConfigLine(cvspath,cfg)
            contents_scm.append(scm_line+'\n')
            if(istag):
                 continue 

            def _ExportLocalSubConfigs(_cvspath,flag_configs,contents_scm,level):
                deps=self.QueryVectorDepsByCVSPath(_cvspath)
                for dep in deps:
                    cfg=self.QueryConfig(dep)
                    cvspath=cfg.CVSPath()
                    flag_configs[cvspath]=True
                    contents_scm.append(TAB_WIDTH*level)
                    (scm_line,istag)=self._GenerateConfigLine(cvspath,cfg)
                    contents_scm.append(scm_line+'\n')
                    if(istag):
                        continue
                    if(cvspath in flag_configs):
                        continue 
                    _ExportLocalSubConfigs(cvspath,flag_configs,contents_scm,level+1)

            _ExportLocalSubConfigs(cvspath,flag_configs,contents_scm,2)
            flag_configs[cvspath]=True

        scm_file='.%s.COMAKE.CONFIGS.SCM'%(self._cvspath.replace('/','.'))
        open(scm_file,'w').writelines(contents_scm)
        self._log_handler.LogNotice("%s[exported local configs info to %s]"%(func_name,scm_file)) 

    def WatchConfigs(self,v):
        """观察COMAKE认为应该使用版本以及本地所使用的版本"""
        for cfg in self._sorted_configs:
            (cvspath,codetag,_)=(cfg.CVSPath(),cfg.CodeTag(),cfg.Revision())
            (localtag,localrev)=self._cs_handler.GetTagAndRevision(cvspath)
            (localtag,localrev_HEAD)=self._cs_handler.GetTagAndHeadRevision(cvspath)
            if((self._scm_handler.IsCodeTagTrivial(localtag) and
                self._scm_handler.IsCodeTagTrivial(codetag) and
                localtag==codetag) or
               ((localtag==codetag) and
                (localrev==localrev_HEAD))):
                print "[cvspath:%s][local:%s][revision:%s][%s]"%(cvspath,
                                                                 localtag,
                                                                 localrev,
                                                                 Function.GreenIt('newest'))
            else:
                print "[cvspath:%s][local:%s][revision:%s][%s][HEAD:%s]"%(cvspath,
                                                                          localtag,
                                                                          localrev,
                                                                          Function.RedIt(codetag),
                                                                          Function.RedIt(localrev_HEAD))
            #打印模块的引入信息.
            if(v>=2):
                print "%s"%(cfg.SerializeToText(0))
            #打印模块的依赖信息.
            if(v>=3):
                deps=self.QueryVectorDepsByCVSPath(cfg.CVSPath())
                for dep in deps:
                    print "\t%s"%(dep)

#GLOBAL VARIABLES.                    
ENV=Environment()
def SetCurrent(env):
    global ENV
    ENV=env

def GetCurrent():
    global ENV
    return ENV
