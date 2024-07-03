#!/usr/bin/env python
#coding:gbk
#Copyright (c) Baidu.com, Inc. All Rights Reserved 
#author:zhangyan04(@baidu.com)

import os
import sys
import Function
import pdb
import json
import ConfigParser
class BaiduBuildSystem(object):
    def __init__(self,env):
        self._env=env
        self._log=env.LogSystem()
        self._make_clean_j='make -j %d -C %s clean'
        self._make_j='make -j %d -C %s'
        self._make_clean='make -C %s clean'
        self._make='make -C %s'
        self._build='cd %s;sh %s'
        self._need_clean=True
        self._make_thread_number=4
        self._BUILDED_TAG='.COMAKE.BUILDED.TAG'
        self._force_build=False
        self._cc_info={}
        self._code_modified={}

    def init_cc_info(self):
        func_name='[_init_cc_info]'
        command='which gcc'
        (status,output,err)=self._log.LogDebugWithCC(
            '%s[cmd:%s]'%(func_name,command),
            command,
            2)
        if status:
            self._log.LogWarning('can not get gcc info, set it as empty')
            output=''
        else:
            output=output.strip()
        self._cc_info={'BIN':output}
     
    def MarkModified(self, cfg):
        self._code_modified[cfg.CVSPath()]=True

    def IsModified(self, cfg):
        if cfg.CVSPath() in self._code_modified:
            return True
        else:
            return False      
  
    def SetNeedClean(self,k):
        self._need_clean=k
        
    def SetMakeThreadNumber(self,k):
        self._make_thread_number=k

    def SetForceBuild(self,k):
        self._force_build=k

    def _FindMakefile(self,cfg):
        basepath=cfg.BasePath(self._env)
        makefile_opts=map(lambda x:os.path.join(basepath,x),
                          ('Makefile','GNUMakefile','makefile'))
        for makefile in makefile_opts:
            if(os.path.exists(makefile)):
                return makefile
        return ''
    
    def _FindBuildScript(self,cfg):
        basepath=cfg.BasePath(self._env)
        build_script_opts=('build.sh',)
        for build_script in build_script_opts:
            if(os.path.exists(os.path.join(basepath,build_script))):                
                return build_script
        return ''

    def _IsMakefileGeneratedByCOMAKE(self,makefile):
        """判断Makefile是否为COMAKE生成的"""
        f=open(makefile).read(len('#COMAKE2')+1)
        if(f.startswith('#COMAKE2')):
            return True
        else:
            return False
        
    def GetDefaultCommands(self,cfg,for_scm):
        """得到构建命令
        1.clean
        2.make
        """
        basepath=cfg.BasePath(self._env)
        (cleancmd,buildcmd) = self._TuneMakeCmd(cfg,for_scm)
        if(buildcmd!= ''):
            return (cleancmd,buildcmd)
        build_script=self._FindBuildScript(cfg)
        if(build_script):
            if(for_scm):
                return ('','sh %s'%build_script)
            else:
                return ('',self._build%(basepath,build_script))
        return ('','')

    def _TuneMakeCmd(self,cfg,for_scm):
        # Tune "make clean;make" to "make clean -j N;make -j N"
        basepath=cfg.BasePath(self._env)
        makefile=self._FindMakefile(cfg)
        if(makefile):
            if(for_scm):
                return ('make clean','make')
            if(self._IsMakefileGeneratedByCOMAKE(makefile)):
                return (self._make_clean_j%(
                        self._make_thread_number,
                        basepath),
                        self._make_j%(
                        self._make_thread_number,
                        basepath))
            else:
                return (self._make_clean%(basepath),
                        self._make%(basepath))
        return ('','')

    def _NeedTuneMakeCmd(self,buildcmd):
        if(buildcmd.endswith('make') \
            and not buildcmd.__contains__('build.sh')):
            return True
        return False

    def _GetCommandFromModuleInfo(self,cfg):
        try:
            config=ConfigParser.ConfigParser()
            config.read('%s/module_info'%cfg.BasePath(self._env))
            data=config.get("module_info", 'build-command-as-dependency')
        except:
            return ''
        return data

    def GetCommands(self,cfg,for_scm=False):
        #1. get from module info
        buildcmd = self._GetCommandFromModuleInfo(cfg)
        if(buildcmd==''):
            #2. get from platform
            buildcmd=cfg.BuildCmd()
        if(buildcmd):
            if(self._NeedTuneMakeCmd(buildcmd)):
                # Do not give up even if not found Makefile given "make clean;make"
                return self.GetDefaultCommands(cfg,for_scm)
            if(for_scm):
                return ('','%s'%(buildcmd))
            else:
                return ('','cd %s;%s'%(cfg.BasePath(self._env),buildcmd))
        #3. deduce from default rule
        return self.GetDefaultCommands(cfg,for_scm)

    def _NeedBuildedByTag(self,builded_tag):
        if(not os.path.exists(builded_tag)):
            return True
        try:
            tag_fp=open(builded_tag,'r')
            data=tag_fp.readlines()
            tag_fp.close()
            data=''.join(data)   
            cc_info=json.loads(data)
            bin_path=cc_info['BIN']
        except:
            # Be pessimistic:(
            return True
        if(bin_path!=self._cc_info['BIN']):
            return True
        try:
            md5sum=cc_info['MD5SUM']
        except:
            # Be pessimistic:(
            return True
        basepath=os.path.dirname(builded_tag)
        cur_md5sum=Function.GenMd5Sum(basepath)
        return cur_md5sum!=md5sum
 
    def NeedBuilded(self,cfg):    
        """检查是否需要构建.下面情况会构建.
        1.强制构建.
        2.不存在BUILDED_TAG这样的文件.
        3.目录下面存在文件比BUILDED_TAG文件新
        """
        if(self._force_build):
            return True
        basepath=cfg.BasePath(self._env)
        builded_tag=os.path.join(basepath,self._BUILDED_TAG)
        if(self._NeedBuildedByTag(builded_tag)):
            return True
        builded_tag_mtime=os.stat(builded_tag)[-2]
        if(Function.CheckDirectoryModified(basepath,builded_tag_mtime)):
            return True
        return False

    def TagBuilded(self,cfg):
        """构建成功后创建文件BUILDED_TAG来标记"""
        basepath=cfg.BasePath(self._env)
        builded_tag=os.path.join(basepath,self._BUILDED_TAG)
        if(os.path.exists(builded_tag)):
            os.remove(builded_tag)
        self._cc_info['MD5SUM']=Function.GenMd5Sum(basepath)
        tag_fp=open(builded_tag,'w')
        tag_fp.write(json.dumps(self._cc_info,sort_keys=True,indent=4))
        tag_fp.close()

    def IgnoredBuild(self,cfg):
        basepath=cfg.BasePath(self._env)
        cvspath=cfg.CVSPath()

        if(cfg.DisableBuild()):
            return (True,'','')

        #NOTICE(zhangyan04)如果是相互前缀的话,那么是不发生编译的.
        abspath1=os.path.abspath(os.getcwd())
        abspath2=os.path.abspath(basepath)
        if(abspath1==abspath2 or
           abspath1.startswith('%s/'%abspath2) or
           abspath2.startswith('%s/'%abspath1)):
            return (True,'','')

        (cleancmd,buildcmd)=self.GetCommands(cfg)
        if(not cleancmd and not buildcmd):
            return (True,'','')

        return (False,cleancmd,buildcmd)
    
    def Build(self,cfg):
        if self._env._cs_handler.HasDiffExists(cfg):
            self.MarkModified(cfg)
        (status,cleancmd,buildcmd)=self.IgnoredBuild(cfg)
        if(status==True):
            self._log.LogNotice('[Action:Build][ignore:%s]'%cfg.CVSPath())
            self.TagBuilded(cfg)
            return
        if not self._env.CodeModified(cfg) and self._env.CacheHit(cfg):
            return
        self._Build(cfg,cleancmd,buildcmd)

    def _Build(self,cfg,cleancmd,buildcmd,rebuild=False):
        if(rebuild==False):
            func_name='[Action:Build]'
        else:
            func_name='[Action:Rebuild]'
        cvspath=cfg.CVSPath()
        #do clean.
        if(cleancmd and 
           self._need_clean):
            command=cleancmd
            (status,_,err)=self._log.LogNoticeWithCC(
                '%s[cvspath:%s][cmd:%s]'%(func_name,
                                          cvspath,
                                          Function.GreenIt(command)),
                command)
            IGNORE_CLEAN_ERROR=True
            if(status):
               if(IGNORE_CLEAN_ERROR):
                   self._log.LogWarning(
                    '%s[cvspath:%s][cmd:%s][status:%d][err:%s]'%(
                        func_name,
                        cvspath,
                        command,
                        status,
                        err))
               else:
                   self._log.LogFatal(
                    '%s[cvspath:%s][cmd:%s][status:%d][err:%s]'%(
                        func_name,
                        cvspath,
                        command,
                        status,
                        err))
                
        #do build.
        if(buildcmd):
            command=buildcmd
            (status,_,err)=self._log.LogNoticeWithCC(
                '%s[cvspath:%s][cmd:%s]'%(func_name,
                                          cvspath,
                                          Function.GreenIt(command)),
                command)
            if(status):
                COMAKE2_MAKEFILE_CHECK_ERROR_250="[comake2_makefile_check] Error 250"
                if(err.__contains__(COMAKE2_MAKEFILE_CHECK_ERROR_250) and rebuild==False):
                    self._log.LogNotice('Build failed due to "%s", trying to work-around it...'%COMAKE2_MAKEFILE_CHECK_ERROR_250)
                    self._TouchMakefile(cvspath,cfg.BasePath(self._env))
                    self._Build(cfg,cleancmd,buildcmd,rebuild=True)
                    return
                else:
                    self._log.LogFatal(
                    '%s[cvspath:%s][cmd:%s][status:%d][err:%s]'%(
                        func_name,
                        cvspath,
                        command,
                        status,
                        err))
        self.TagBuilded(cfg)
        self._env.ToCache(cfg)

    def BuildonFork(self,cfg):
        if self._env._cs_handler.HasDiffExists(cfg):
            self.MarkModified(cfg)   
        func_name='[Action:BuildonFork]'
        (status,cleancmd,buildcmd)=self.IgnoredBuild(cfg)
        if(status==True):
            self._log.LogNotice('%s[ignore:%s]'%(func_name,
                                                 cfg.CVSPath()))
            self.TagBuilded(cfg)
            return -1

        pid = os.fork()
        if pid == 0:
            #self._env.set_signal_handler()
            if not self._env.CodeModified(cfg) and self._env.CacheHit(cfg):
                sys.exit(0)
            self._Build(cfg,cleancmd,buildcmd)
            sys.exit(0)
        elif pid == -1:
            msg='Fail to fork'
            self._log.LogFatal('%s%s'%(func_name,msg))
        else:
            return pid

    def _TouchMakefile(self,cvspath,basepath):
        func_name='[Action:_TouchMakefile]'
        command='find %s -name Makefile -exec touch {} \;'%basepath
        (status,_,err)=self._log.LogNoticeWithCC(
                '%s[cvspath:%s][cmd:%s]'%(func_name,
                                          cvspath,
                                          Function.GreenIt(command)),
                command)
        if(status):
            self._log.LogFatal(
                    '%s[cvspath:%s][cmd:%s][status:%d][err:%s]'%(
                        func_name,
                        cvspath,
                        command,
                        status,
                        err))
        return

 
