#!/usr/bin/env python
#coding:gbk
#Copyright (c) Baidu.com, Inc. All Rights Reserved 
#author:zhangyan04(@baidu.com)

import os
import sys
import getopt
import glob
import ConfigParser

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import MakefileWriter
import Environment
import Scratch
import Function
from Syntax import *
from Environment import ENV
import pdb
import CheckCOMAKE 
import Scmbuild
import CodeSystem
import Analyzer
WATCH_CONFIGS=0
UPDATE_CONFIGS=False
DUMP_CONFIGS=False
BUILD_CONFIGS=False
MAKE_SCRATCH=False
Reference_REV=''
EXPORT_CONFIGS=False
EXPORT_ARGV=''
RECURSIVE_GEN_MAKEFILE=True
SCM_FILE=''
EXPORT_FILE=''
CONF_FILE=''
SCM_AUDIT=0
DEV_DIFF=0
USER_SET_MODULE_THREADS=False
USER_SET_NEW_DA=False
EXPORT_LOCAL_CONFIGS=False

#读取版本号信息.
VERSION=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              'COMAKE.VERSION')).read()

#帮助信息.
HELP="""comake[com make]能够自动帮助用户搭建环境,并且生成Makefile工具.
程序会读取目录下面的COMAKE文件,产生Makefile和环境.用户需要提供这个COMAKE文件.
版本:%s
参数:
        -h --help 查看帮助
        -D --debug 开启debug选项[默认不打开].-D -D可以查看更多调试信息.
        -S --scratch 创建一个默认的COMAKE文件
        -r --revision 从平台检出模块cvspath指定的TAG对应的依赖列表，配合-S使用，如-S -r 1.0.0.0
        -E --export-configs 导出模块的4位版本依赖,存放在COMAKE.CONFIGS下面.比如-E public/ub@1.0.0.0
        -W --watch-configs 查看本地依赖模块.-W -W可以查看模块引入来源.-W -W -W可以查看依赖模块的依赖.
        -I --import-files 在解释COMAKE文件之前导入模块
        -C --change directory 切换到directory下面执行[默认当前目录]
        -Q --quiet 安静模式[默认不打开]
        -U --update-configs 更新环境
        -B --build-configs 构建环境
        -F --force 构建环境时强制进行[默认不进行]
        -e --export-local-configs 导出本地环境到CONFIGS.SCM文件
        -f --scmfile= 重现编译环境
        -d --devdiff 存在本地修改的共同开发依赖列表（多模块共同开发时适用）
        -J --make-thread-number= 如果模块使用COMAKE生成的Makefile的话,编译线程数[默认是4]
        -j --modules-thread-number= 并发下载、编译模块的线程数[默认是1]
        -K --keep-going 构建/更新环境中途出错的话,忽略错误继续[已废弃]
        -P --pretreatment 生成Makefile时不进行预处理[默认进行预处理]
        -O --quot-all-deps 生成Makefile时引用所有头文件依赖[默认过滤目录外依赖]
        --no-recursive 不递归生成每个目录下面的Makefile[默认情况下是递归生成]
        --no-revert 不恢复依赖模块的本地修改，配合-U使用[默认恢复]
        --time-compile-link 计时编译和链接时间[默认不打开]
        --recache 强制更新comake2缓存的依赖列表
        --old-da  使用2.1.2及以前的依赖打平策略
        --new-da  最新打平策略[默认，详情请访问http://wiki.babel.baidu.com/twiki/bin/view/Com/Pmo/Scm/Comake2guide#依赖打平策略]
"""

def usage():
    print HELP%(VERSION)

def process_args():
    """处理参数"""
    try:
        #-N选项已经不再使用,作为遗留选项处理.
        opts,args=getopt.getopt(sys.argv[1:],"hDSr:E:I:C:QWBUPOKJ:j:Ff:NRAde",
                                ["help",
                                 "debug",
                                 "scratch",
                                 "revision=",
                                 "export-configs=",
                                 "import-files=",
                                 "change=",
                                 "quiet",
                                 "watch-configs",
                                 "update-configs",
                                 "build-configs",
                                 "pretreatment",
                                 "quot-all-deps",
                                 "force",
                                 "scmfile=",
                                 "export=",
                                 "keep-going",
                                 "no-recursive",
                                 "no-revert",
                                 "recache",
                                 "time-compile-link",
                                 "build-shared-library",
                                 "warn-newer-cfgs",
                                 "conf=",
                                 "scmaudit",
                                 "devdiff",
                                 "new-da",
                                 "old-da",
                                 "export-local-configs",
                                 "modules-thread-number=",
                                 "make-thread-number=",
                                 "dump-da=",
                                 "dd=",
                                 "dump-cfgs"])
    except getopt.GetoptError,_:
        usage()
        sys.exit(-1)
        
    global WATCH_CONFIGS
    global UPDATE_CONFIGS
    global DUMP_CONFIGS
    global BUILD_CONFIGS
    global MAKE_SCRATCH
    global Reference_REV
    global EXPORT_CONFIGS
    global EXPORT_ARGV
    global RECURSIVE_GEN_MAKEFILE
    global SCM_FILE
    global EXPORT_FILE
    global CONF_FILE
    global SCM_AUDIT
    global DEV_DIFF
    global USER_SET_MODULE_THREADS
    global USER_SET_NEW_DA
    global EXPORT_LOCAL_CONFIGS

    env=Environment.GetCurrent()
    for (k,v) in opts:
        if(k in ("-h","--help")):
            usage()
            sys.exit(0)
        elif(k in ("-D",'--debug')):
            env.LogSystem().IncDebugLevel()
        elif(k=='--dump-da'):
            if(v=='da'):
                env.DepSystem().EnableDumpDA()
            elif(v=='dc'):
                env.DepSystem().EnableDumpCollected()
            elif(v=='df'):
                env.DepSystem().EnableDumpFlatten()
            elif(v=='ds'):
                env.DepSystem().EnableDumpSorted()
            elif(v=='dm'):
                env.DepSystem().EnableDumpMap()
            else:
                env.LogSystem().LogFatal('--dump-da=%s not supported, specify --dump-da=da|dc|df|dm|ds'%v)
        elif(k in ("-S","--scratch")):
            MAKE_SCRATCH=True
        elif(k in ("-r","--revision")):
            Reference_REV=v
        elif(k in ("-E","--export-configs")):
            EXPORT_CONFIGS=True
            EXPORT_ARGV=v
        elif(k in ("-I","--import-files")):
            env.AppendImportFile(os.path.abspath(v))
        elif(k in ("-C","--change")):
            env.SetChangeDir(os.path.abspath(v))
        elif(k in ("-Q","--quiet")):
            env.LogSystem().SetQuiet()
        elif(k in ("-W",'--watch-configs')):
            WATCH_CONFIGS+=1
        elif(k in ('-U','--update-configs')):
            UPDATE_CONFIGS=True
        elif(k in ('-P',"--pretreatment")):
            oper_add_env('PRE','True')  
        elif(k in ('-O','--quot-all-deps')):
            oper_add_env('QUOT_ALL_DEPS','True')  
        elif(k in ('-B','--build-configs')):
            BUILD_CONFIGS=True
        elif(k in ('-F','--force')):
            env.BuildSystem().SetForceBuild(True)
        elif(k in ('-f','--scmfile')):
            SCM_FILE=v
        elif(k in ('-e','--export-local-configs')):
            EXPORT_LOCAL_CONFIGS=True
        elif(k=='--export'):
            EXPORT_FILE=v
        elif(k in ('-A','--scmaudit')):
            SCM_AUDIT+=1
        elif(k in ('-d','--devdiff')):
            env.LogSystem().SetQuiet()
            DEV_DIFF+=1
        elif(k=='--new-da'):
            env.SetNewDA(True)
            USER_SET_NEW_DA=True
        elif(k=='--old-da'):
            env.SetNewDA(False)
            USER_SET_NEW_DA=True
        elif(k=='--conf'):
            CONF_FILE=v
        elif(k in ('-K','--keep-going')):
            msg='-K选项已废弃'
            env.LogSystem().LogFatal(msg) 
        elif(k in ('-J',"--make-thread-number")):
            env.BuildSystem().SetMakeThreadNumber(int(v))
            env.TaskThreadPool().SetLimit(int(v))
        elif(k in ('-j',"--modules-thread-number")):
            env.CodeSystem().SetParallelUpdates(int(v))
            env.SetParallelBuilds(int(v))
            USER_SET_MODULE_THREADS=True
        elif(k=="--no-recursive"):
            RECURSIVE_GEN_MAKEFILE=False
        elif(k=="--no-revert"):
            env.CodeSystem().SetNoRevert(True)
        elif(k=="--time-compile-link"):
            env.SetTimeCompileLink(True)            
        elif(k=="--recache"):
            env.SetReCache(True)
        elif(k=="--warn-newer-cfgs"):
            env.SetWarnNewerCfgs(True)
        elif(k=="--dd"):
            # --dd and --dump-cfgs share same mode when analyzing deps.
            DUMP_CONFIGS=True
            env.SetDiffConfigs(v)
            env.SetDumpCfgs(True)
            env.LogSystem().SetQuiet()
        elif(k=="--dump-cfgs"):
            DUMP_CONFIGS=True
            env.SetDumpCfgs(True)
        #    env._log_handler.SetQuiet()
    return 

def interpret():
    env=Environment.GetCurrent()
    for f in env.ImportFiles():
        execfile(f)
    if(not os.path.exists('COMAKE')):
        msg='COMAKE: no such file under %s'%os.getcwd()
        env.LogSystem().LogFatal(msg)
    execfile('COMAKE')

def interpret_configs():
    env=Environment.GetCurrent()
    targetstring=''
    for f in env.ImportFiles():
        targetstring+=env.InterpretConfigsFromCOMAKE(f)
    targetstring+=env.InterpretConfigsFromCOMAKE('COMAKE')
    return targetstring

def interpret_targets(targetstring):
    #in case targetstring contains '\r\n'
    targetstring='\n'.join(targetstring.splitlines())+'\n'
    env=Environment.GetCurrent()
    env.LogSystem().LogDebug(targetstring)
    exec(targetstring)

def handle(mkwr):
    env=Environment.GetCurrent()
    env.Clear()
    targetstring=interpret_configs()
    env.ActionConfigs()
    env.ActionDepends()
    interpret_targets(targetstring)
    env.Action()
    mkwr.Collect(env)
    return

def get_svn_server(conf_file):
    try:
        config=ConfigParser.ConfigParser()
        config.read(conf_file)
        svn_server=config.get("general","svn")
    except:
        svn_server='https://svn.baidu.com'
    return svn_server

def get_parallel_update_limit(conf_file):
    try:
        config=ConfigParser.ConfigParser()
        config.read(conf_file)
        parallel_update_limit=int(config.get("advanced","parallel-updates"))
    except:
        parallel_update_limit=0
    return parallel_update_limit

def get_parallel_build_limit(conf_file):
    try:
        config=ConfigParser.ConfigParser()
        config.read(conf_file)
        parallel_build_limit=int(config.get("advanced","parallel-builds"))
    except:
        parallel_build_limit=0
    return parallel_build_limit

def get_cpp_disabled_flag(conf_file):
    try:
        config=ConfigParser.ConfigParser()
        config.read(conf_file)
        disabled=(config.get("advanced","disable-cpp")=="yes")
    except: 
        disabled=False
    return disabled

def enable_module_cache(conf_file):
    try:
        config=ConfigParser.ConfigParser()
        config.read(conf_file)
        enabled=(config.get("advanced","enable-module-cache")=="yes")
    except:
        env=Environment.GetCurrent()
        enabled=env.EnableModuleCache()
    return enabled

def enable_new_da(conf_file):
    try:
        config=ConfigParser.ConfigParser()
        config.read(conf_file)
        enabled=(config.get("advanced","enable-new-da")=="yes")
    except:
        env=Environment.GetCurrent()
        enabled=env.NewDA()
    return enabled

def read_conf():
    env=Environment.GetCurrent()
    found_conf=True
    global CONF_FILE
    global USER_SET_MODULE_THREADS
    if(CONF_FILE):
        conf_file=os.path.expanduser(CONF_FILE)
        if(not os.path.exists(conf_file)):
            env.LogSystem().LogFatal('conf file %s not exists'%conf_file)
    else:
        conf_file=os.environ['HOME']+'/.comake2.conf'
        if(not os.path.exists(conf_file)):
            conf_file=sys.path[0]+'/comake2.conf'
            if(not os.path.exists(conf_file)):
                found_conf=False
    if(found_conf):
        CodeSystem.SVN_SERVER=get_svn_server(conf_file)
        if(not USER_SET_MODULE_THREADS):
            parallel_update_limit=get_parallel_update_limit(conf_file)
            env.CodeSystem().SetParallelUpdates(parallel_update_limit)
            parallel_build_limit=get_parallel_build_limit(conf_file)
            env.SetParallelBuilds(parallel_build_limit)
        env.SetEnableModuleCache(enable_module_cache(conf_file))
        if(not USER_SET_NEW_DA):
            env.SetNewDA(enable_new_da(conf_file))
        if(get_cpp_disabled_flag(conf_file)==True):
            oper_add_env('PRE','True')  
        env.LogSystem().LogDebug('Parsed conf file %s'%conf_file)

def comake_main():
    cwd=os.getcwd()    
    env=Environment.GetCurrent()
    os.chdir(env.ChangeDir())

    read_conf()

    global SCM_FILE
    global EXPORT_FILE
    global UPDATE_CONFIGS
    global BUILD_CONFIGS
    if(SCM_FILE):
        scmbuild=Scmbuild.Scmbuild(env,SCM_FILE)
        if(EXPORT_FILE):
            scmbuild.Export(EXPORT_FILE)
        elif(UPDATE_CONFIGS == BUILD_CONFIGS):
            scmbuild.Update()
            scmbuild.Build()
        elif(UPDATE_CONFIGS):
            scmbuild.Update()
        elif(BUILD_CONFIGS):
            scmbuild.Build()
        return

    global DEV_DIFF
    if(DEV_DIFF):
        env.Clear()
        interpret()
        env.ImportConfigsFromSubDirectories()
        env.CollectDevDiffs()
        return

    #1.生成COMAKE文件.
    global MAKE_SCRATCH
    global Reference_REV
    if(MAKE_SCRATCH):
        Scratch.scratch(env,Reference_REV)
        return
    
    #2.导出CONFIGS文件.
    #导出的位置为COMAKE.CONFIGS.
    global EXPORT_CONFIGS
    global EXPORT_ARGV
    if(EXPORT_CONFIGS):
        env.ExportConfigs(EXPORT_ARGV)
        return

    #2.查看依赖模块版本.
    global WATCH_CONFIGS
    if(WATCH_CONFIGS):
        env.Clear()
        interpret()
        env.ImportConfigsFromSubDirectories()
        env.ActionConfigs()
        env.WatchConfigs(WATCH_CONFIGS)
        return

    global EXPORT_LOCAL_CONFIGS
    if(EXPORT_LOCAL_CONFIGS):
        env.Clear()
        interpret()
        env.ImportConfigsFromSubDirectories()
        env.ActionConfigs()
        #导出当前所使用的依赖.
        env.ExportLocalConfigs()
        return

    global SCM_AUDIT
    env.SetScmAudit(SCM_AUDIT)
    env.SetReferenceREV(Reference_REV)

    global DUMP_CONFIGS
    if(DUMP_CONFIGS):
        env.Clear()
        interpret()
        env.ImportConfigsFromSubDirectories()
        env.ActionConfigs()
        return

    #3.尝试更新/构建环境
    if(UPDATE_CONFIGS or
       BUILD_CONFIGS):
        #更新 & 构建环境.
        if(UPDATE_CONFIGS and
           BUILD_CONFIGS):
            env.Clear()
            interpret()
            env.ImportConfigsFromSubDirectories()
            env.SetDoingUpdate(True)
            env.ActionConfigs()
            #导出当前所使用的依赖.
            env.ExportLocalConfigs()
            env.BuildConfigs()
            
        #只是更新环境.
        elif(UPDATE_CONFIGS):
            env.Clear()
            interpret()
            env.ImportConfigsFromSubDirectories()
            env.SetDoingUpdate(True)
            env.ActionConfigs()
            #导出当前所使用的依赖.
            env.ExportLocalConfigs()

        #只是构建环境.
        else:
            env.Clear()
            interpret()
            env.ImportConfigsFromSubDirectories()
            env.ActionConfigs()
            env.BuildConfigs()
        return 
    
    #5.生成Makefile.
    generate_makefile()
    os.chdir(cwd)
    oper_del_env('PRE')
    oper_del_env('QUOT_ALL_DEPS')


def generate_makefile():
    func_name='[Action:generate_makefile]'
    env=Environment.GetCurrent()
    mkwr=MakefileWriter.MakefileWriter()
    handle(mkwr)
    mkwr.Write()
    #导出当前所使用的依赖.
    #env.ExportLocalConfigs()

    global RECURSIVE_GEN_MAKEFILE
    if(not RECURSIVE_GEN_MAKEFILE):
        return 

    #Handle Subdirectories.
    subdirs=env.SubDirectories()
    workdir=env.ChangeDir()
    cwd=os.getcwd()
    for subdir in subdirs:
        env.LogSystem().LogNotice(
            '%s[enter directory:%s]'%(func_name,
                                      subdir))        
        workpath=os.path.join(workdir,subdir)        
        os.chdir(workpath)        
        if(os.path.exists('COMAKE')):
            generate_makefile()
        os.chdir(cwd)
        env.LogSystem().LogNotice(
            '%s[leave directory:%s]'%(func_name,
                                      subdir))
def oper_add_env(env_name,env_value): 
    os.environ[env_name]=env_value
def oper_del_env(env_name):
    if os.environ.keys().__contains__(env_name):
        os.environ.__delitem__(env_name)
def main():
    process_args()
    comake_main()
    env=Environment.GetCurrent()
    analyzer=Analyzer.Analyzer(env)
    analyzer.analyze_log()

    
if __name__=='__main__':
    main()
