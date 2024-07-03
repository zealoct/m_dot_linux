#!/usr/bin/env python
#coding:gbk
#Copyright (c) Baidu.com, Inc. All Rights Reserved 
#author:hailijuan(@baidu.com)

import Config
import sys

collected_compile_deps_cache=dict()

DUMP_COLLECTED_FLAG=False
DUMP_FLATTEN_FLAG=False
DUMP_MAP_FLAG=False
DUMP_SORTED_FLAG=False

class BaiduDepAlgorithm(object):
    def __init__(self,env):
        self._env=env
        self._flatten_compile_deps_cache=dict()
        self._flatten_compile_args_cache=dict()
        self._map_direct_configs=dict()
        self._sorted_configs=list()
        self._map_configs_deps=dict()

    def DepAlgorithm(self,root_cfg):
        func_name='[DepAlgorithm]'
        if(self._env.CodeSystem().EnableParallelUpdates()):
            self._env.LogSystem().SetParallelMode(True)
        self._CollectConfigs(root_cfg)
        if(self.DumpCollected()==True):
            contents_scm=list()
            contents_scm.append('===DumpCollectedConfigs===')
            self.DumpCollectedConfigs(root_cfg,depth=0,dump_flags=dict(),contents=contents_scm)
            scm_file='.%s.001.dc'%(self._env.CVSPath().replace('/','.'))
            open(scm_file,'w').write('\n'.join(contents_scm)+'\n')
            self._env.LogSystem().LogNotice("%s[exported collected configs info to %s]"%(func_name,scm_file))

        (cvspath,codetag,depstag,revision,athead)=(root_cfg.CVSPath(),
                                   root_cfg.CodeTag(),
                                   root_cfg.DepsTag(),
                                   root_cfg.Revision(),
                                   root_cfg.AtHEAD())
        key=self._env.SCMSystem().GetDepKey(cvspath,codetag,depstag,revision,athead)
        (self._flatten_compile_deps_cache[key],
         self._flatten_compile_args_cache[key])=self._FlattenConfigs(root_cfg)
        if(self.DumpFlatten()==True):
            contents_scm=self.DumpFlattenConfigs(root_cfg)
            scm_file='.%s.002.df'%(self._env.CVSPath().replace('/','.'))
            open(scm_file,'w').write('\n'.join(contents_scm)+'\n')
            self._env.LogSystem().LogNotice("%s[exported flattened configs info to %s]"%(func_name,scm_file))
        
        self._FillMapDirectConfigs(root_cfg)
        for cfg in self._flatten_compile_deps_cache[key]:
            self._FillMapDirectConfigs(cfg)
        if(self.DumpMap()==True):
            contents_scm=self.DumpMapConfigs()
            scm_file='.%s.003.dm'%(self._env.CVSPath().replace('/','.'))
            open(scm_file,'w').write('\n'.join(contents_scm)+'\n')
            self._env.LogSystem().LogNotice("%s[exported mapped configs info to %s]"%(func_name,scm_file))

        self._FillConfigArgs(root_cfg)
        self._FillConfigDepth(root_cfg)

        sorted_configs_flags=dict()
        sorted_configs_by_cvspath=list()
        self._SortConfigsByCVSPath(cvspath,sorted_configs_flags,sorted_configs_by_cvspath)
        for cvspath in sorted_configs_by_cvspath:
            cfg=self._GetConfigByCVSPath(self._flatten_compile_deps_cache[key],cvspath)
            if(cfg==None):
                self._env.LogSystem().LogFatal('%s[%s not exists]'%(func_name,cvspath))
            self._sorted_configs.append(cfg)
        if(self.DumpSorted()==True):
            contents_scm=self.DumpSortedConfigs(root_cfg)
            scm_file='.%s.004.ds'%(self._env.CVSPath().replace('/','.'))
            open(scm_file,'w').write('\n'.join(contents_scm)+'\n')
            self._env.LogSystem().LogNotice("%s[exported sorted configs info to %s]"%(func_name,scm_file))

        #for backward-compat
        self._FillMapConfigsDeps(root_cfg)
        for cfg in self._flatten_compile_deps_cache[key]:
            self._FillMapConfigsDeps(cfg)
        self._env._sorted_configs=self._sorted_configs
        for cvspath in self._map_configs_deps.keys():
            self._env._map_configs_deps[cvspath]=(self._map_configs_deps[cvspath],'')
        for cfg in self._env._sorted_configs:
            self._env._map_configs[cfg.CVSPath()]=cfg
        self._env._configs=self._sorted_configs
        #map_configs_root affect code updating and dep info exporting.
        self._env._FillMapConfigsRoot()

        if(self._env.DoingUpdate()):
            self._GetRemoteRevision()
        self._env.LogSystem().SetParallelMode(False)

    def _CollectConfigs(self,root_cfg):
        (configs,_)=self._ParseDirectConfigs(root_cfg)
        for cfg in configs:
            if(cfg.DisableBuild()==False \
                and self._env.SCMSystem().IsTagCOMAKE(cfg.DepsTag())):
                self._CollectConfigs(cfg)
        return

    def _ParseDirectConfigs(self,cfg):
        return self._env.SCMSystem().GetCompileDepsAndArgs(cfg.CVSPath(),
                                                     cfg.CodeTag(),
                                                     cfg.DepsTag(),
                                                     cfg.Revision(),
                                                     cfg.AtHEAD())

    def GetOrInitConfigFromArgs(self,cvspath,codetag,revision,
                            depstag,args,buildcmd,status,env):
        if(self._env.SCMSystem().IsTagTrunk(codetag) \
            or self._env.SCMSystem().IsTagBranch(codetag)):
            if(self._env.ExistsConfigASH(cvspath)):
                config_ash=self._env.QueryConfigASH(cvspath)
                codetag=config_ash.CodeTag()
                revision=config_ash.Revision()
        key='%s@%s@%s'%(cvspath,codetag,revision)
        if(self._env.NewDA()==True and key in collected_compile_deps_cache):
            cfg=collected_compile_deps_cache[key]
            if(cfg.DepsTag()!=depstag):
                if(self._env.SCMSystem().IsTagNull(cfg.DepsTag()) \
                    or self._env.SCMSystem().IsTagCOMAKE(depstag)):
                    self._env.LogSystem().LogWarning('Dep conflicting: %s@%s@%s changed to %s@%s@%s'%(
                                        cvspath,codetag,cfg.DepsTag(),
                                        cvspath,codetag,depstag))
                    cfg.SetDepsTag(depstag)
                else:
                    self._env.LogSystem().LogWarning('Dep conflicting: %s@%s@%s collected before, %s@%s@%s ignored'%(
                                        cvspath,codetag,cfg.DepsTag(),
                                        cvspath,codetag,depstag))
            return cfg
        cfg=Config.Config()
        cfg.InitFromArgs(cvspath,
                     codetag,
                     revision,
                     depstag,
                     args,
                     buildcmd,
                     status,
                     revision=='', #atHEAD
                     env)
        collected_compile_deps_cache[key]=cfg
        return cfg

    def QueryConfig(self,cvspath,codetag,revision):
        key='%s@%s@%s'%(cvspath,codetag,revision)
        return collected_compile_deps_cache[key]

    def _GetRemoteRevision(self):
        self._env.LogSystem().LogNotice('Getting remote revisions from svn server ...')
        for cfg in self._sorted_configs:
            self._env.CodeSystem().GetRemoteRevision(cfg)
        if(self._env.CodeSystem().WaitOtherUpdatesFinish()!=0):
            sys.exit(1)

    def _FlattenConfigs(self,root_cfg): 
        (direct_configs,direct_args)=self._ParseDirectConfigs(root_cfg)
        if(not self._env.SCMSystem().IsTagCOMAKE(root_cfg.DepsTag()) \
            and root_cfg.DisableBuild()==False):
            (cvspath,codetag,depstag,revision,athead)=(root_cfg.CVSPath(),
                                   root_cfg.CodeTag(),
                                   root_cfg.DepsTag(),
                                   root_cfg.Revision(),
                                   root_cfg.AtHEAD())
            key=self._env.SCMSystem().GetDepKey(cvspath,codetag,depstag,revision,athead)
            self._flatten_compile_deps_cache[key]=direct_configs
            self._flatten_compile_args_cache[key]=direct_args
            return (direct_configs,direct_args)
        merged_configs=list()
        merged_args=direct_args
        for cfg in direct_configs:
            if(cfg.DisableBuild()==True):
                merged_configs.append(cfg)
                continue
            (cvspath,codetag,depstag,revision,athead)=(cfg.CVSPath(),
                                   cfg.CodeTag(),
                                   cfg.DepsTag(),
                                   cfg.Revision(),
                                   cfg.AtHEAD())
            key=self._env.SCMSystem().GetDepKey(cvspath,codetag,depstag,revision,athead) 
            if(key in self._flatten_compile_deps_cache):
                flatten_configs=self._flatten_compile_deps_cache[key]
                flatten_args=self._flatten_compile_args_cache[key]
            else:
                (flatten_configs,flatten_args)=self._FlattenConfigs(cfg)
                self._flatten_compile_deps_cache[key]=flatten_configs
                self._flatten_compile_args_cache[key]=flatten_args
            merged_configs.extend(flatten_configs) 
            merged_configs.append(cfg)
            for cvspath in flatten_args.keys():
                if(cvspath in direct_args):
                    continue
                elif(cvspath in merged_args):
                    merged_args[cvspath]=merged_args[cvspath]+flatten_args[cvspath]
                else:
                    merged_args[cvspath]=flatten_args[cvspath]
        merged_configs=list(set(merged_configs))
        self._FlattenConfigsAfterSubDepsFlatten(root_cfg,direct_configs,merged_configs)
        return (merged_configs,merged_args)

    def _FlattenConfigsAfterSubDepsFlatten(self,root_cfg,direct_configs,merged_configs):
        func_name='[ConfigsFlatten]'
        del_configs=list()
        cvspath_dict=dict()
        for i in range(0,len(merged_configs)):
            cvspath=merged_configs[i].CVSPath()
            if(cvspath in cvspath_dict):
                cvspath_dict[cvspath].append(merged_configs[i])
            else:
                cvspath_dict[cvspath]=[merged_configs[i]]
        for collects in cvspath_dict.values():
            if(len(collects)==1):
                continue
            chosen_config=self._ResolvedConflictingConfigs(direct_configs,collects)
            msg='%s[Choosed %s:%s]'%(func_name,chosen_config.CVSPath(),chosen_config.CodeTag())
            self._env.LogSystem().LogDebug(msg) 
            for cls in collects:
                msg='    %s:%s'%(cls.CVSPath(),cls.CodeTag())
                self._env.LogSystem().LogDebug(msg) 
            for cfg in collects:
                if(cfg==chosen_config):
                    continue
                del_configs.append(cfg)
        for cfg in del_configs:
            merged_configs.remove(cfg)

    def _FillConfigArgs(self,cfg):
        if(cfg.DisableBuild()==True):
            return
        (cvspath,codetag,depstag,revision,athead)=(cfg.CVSPath(),
                                   cfg.CodeTag(),
                                   cfg.DepsTag(),
                                   cfg.Revision(),
                                   cfg.AtHEAD())
        key=self._env.SCMSystem().GetDepKey(cvspath,codetag,depstag,revision,athead)
        flatten_cfgs=self._flatten_compile_deps_cache[key]
        flatten_args=self._flatten_compile_args_cache[key]
        for cfg in flatten_cfgs:
             cvspath=cfg.CVSPath()
             if cvspath in flatten_args:
                 args=flatten_args[cvspath]
             else:
                 args=list()
             cfg.ParseArgs(args)

    def _FillConfigDepth(self,cfg):
        if(cfg.DisableBuild()==True):
            return
        (cvspath,codetag,depstag,revision,athead)=(cfg.CVSPath(),
                                   cfg.CodeTag(),
                                   cfg.DepsTag(),
                                   cfg.Revision(),
                                   cfg.AtHEAD())
        key=self._env.SCMSystem().GetDepKey(cvspath,codetag,depstag,revision,athead)
        direct_cfgs=self._ParseDirectConfigs(cfg)[0]
        for subcfg in self._flatten_compile_deps_cache[key]:
            if(subcfg in direct_cfgs):
                subcfg.SetDepth(1)
            else:
                subcfg.SetDepth(2)

    def _GetConfigByCVSPath(self,configs,cvspath):
        for cfg in configs:
            if(cfg.CVSPath()==cvspath):
                return cfg
        return None

    def _SortConfigsByCVSPath(self,cvspath,sorted_configs_flags,sorted_configs_by_cvspath):
        cvspath_list=self._map_direct_configs[cvspath]
        for sub_cvspath in cvspath_list:
            if(not sub_cvspath in self._map_direct_configs):
                self._env.LogSystem().LogWarning('%s ignored by purpose, may have no need of it otherwise add it in dep list. append --dump-da=da for details'%sub_cvspath)
                continue
            self._SortConfigsByCVSPath(sub_cvspath,sorted_configs_flags,sorted_configs_by_cvspath)
            if(sub_cvspath in sorted_configs_flags):
                continue
            sorted_configs_by_cvspath.append(sub_cvspath)
            sorted_configs_flags[sub_cvspath]=True

    def _FillMapConfigsDeps(self,root_cfg):
        cvspath=root_cfg.CVSPath()
        if(cvspath in self._map_configs_deps):
            return
        self._map_configs_deps[cvspath]=list()
        if(root_cfg.DisableBuild()==True):
            return
        (codetag,depstag,revision,athead)=(root_cfg.CodeTag(),
                                   root_cfg.DepsTag(),
                                   root_cfg.Revision(),
                                   root_cfg.AtHEAD())
        key=self._env.SCMSystem().GetDepKey(cvspath,codetag,depstag,revision,athead)
        configs=self._flatten_compile_deps_cache[key]
        for cfg in configs:
            self._map_configs_deps[cvspath].append(cfg.CVSPath())

    def _FillMapDirectConfigs(self,root_cfg):
        cvspath=root_cfg.CVSPath()
        self._map_direct_configs[cvspath]=list()
        if(root_cfg.DisableBuild()==True):
            return
        configs=self._ParseDirectConfigs(root_cfg)[0]
        for cfg in configs:
            self._map_direct_configs[cvspath].append(cfg.CVSPath())
        # update self._map_configs_deps.
        if(not self._env.SCMSystem().IsTagCOMAKE(root_cfg.DepsTag()) \
            and not cvspath in self._map_configs_deps):
            self._map_configs_deps[cvspath]=list()
            for cfg in configs:        
                self._map_configs_deps[cvspath].append(cfg.CVSPath())

    def _PickDirectDepFromCollects(self,deps,collects):
        for dep in deps:
            if(dep in collects):
                return dep
        return None

    def _ResolvedConflictingConfigs(self,direct_configs,collects):
        first_dir_dep=self._PickDirectDepFromCollects(direct_configs,collects)
        if(first_dir_dep!=None):
        # 1. If direct-dep conflicts with indirect-dep, choose direct-dep.
            return first_dir_dep

        # 2. If indirect-deps conflict with each othter, choose newer version.
        for i in range(0,1):
            #1.首先检查是否均为常规4位TAG
            all_4_tag=True
            for cfg in collects:
                if(not self._env.SCMSystem().IsCodeTagTrivial(cfg.CodeTag())):
                    all_4_tag=False
                    break
            if(not all_4_tag):
                self._ReportUnresolvedConflicts(collects)
                
            #2.选择标号最大的内容.
            numbers=map(lambda x:self._env.SCMSystem().Tag2Number(x.CodeTag()),
                        collects)            
            max_number=max(numbers)
            collects=filter(
                lambda x:self._env.SCMSystem().Tag2Number(x.CodeTag())==max_number,
                collects)
            if(len(collects)<2):
                return collects[0]
                
            #3.选择指定了objects的内容
            tmp_collects=filter(lambda x:x.Objects(),collects)
            if(tmp_collects):
                collects=tmp_collects
            if(len(collects)<2):
                return collects[0]

            #4.没有办法处理冲突了.
            self._ReportUnresolvedConflicts(collects)

    def _ReportUnresolvedConflicts(self,collects):
        self._env.LogSystem().LogWarning(
                "==========[Conflict:%s]=========="%(collects[0].CVSPath()))
        for cfg in collects:
                self._env.LogSystem().LogWarning("===%s@%s"%(cfg.CVSPath(),cfg.CodeTag()))
        self._env.LogSystem().LogFatal('Please fix the conflict!') 

    def EnableDumpDA(self):
        global DUMP_COLLECTED_FLAG
        global DUMP_FLATTEN_FLAG
        global DUMP_MAP_FLAG
        global DUMP_SORTED_FLAG
        DUMP_COLLECTED_FLAG=True
        DUMP_FLATTEN_FLAG=True
        DUMP_MAP_FLAG=True
        DUMP_SORTED_FLAG=True

    def EnableDumpCollected(self):
        global DUMP_COLLECTED_FLAG
        DUMP_COLLECTED_FLAG=True

    def EnableDumpFlatten(self):
        global DUMP_FLATTEN_FLAG
        DUMP_FLATTEN_FLAG=True

    def EnableDumpMap(self):
        global DUMP_MAP_FLAG
        DUMP_MAP_FLAG=True

    def EnableDumpSorted(self):
        global DUMP_SORTED_FLAG
        DUMP_SORTED_FLAG=True

    def DumpCollected(self):
        return DUMP_COLLECTED_FLAG

    def DumpFlatten(self):
        return DUMP_FLATTEN_FLAG

    def DumpMap(self):
        return DUMP_MAP_FLAG

    def DumpSorted(self):
        return DUMP_SORTED_FLAG

    def DumpAllConfigs(self):
        for cfg in collected_compile_deps_cache.values():
            print '%s@%s'%(cfg.CVSPath(),cfg.CodeTag())
 
    def DumpCollectedConfigs(self,cfg,depth,dump_flags,contents):
        TAB_WIDTH=' '*4
        contents.append('%s%s@%s@%s'%(TAB_WIDTH*depth,cfg.CVSPath(),cfg.CodeTag(),cfg.DepsTag()))
        #print '%s%s@%s@%s'%(TAB_WIDTH*depth,cfg.CVSPath(),cfg.CodeTag(),cfg.DepsTag())
        for subcfg in self._ParseDirectConfigs(cfg)[0]:
            if(subcfg in dump_flags or subcfg.DisableBuild()==True):
                continue
            self.DumpCollectedConfigs(subcfg,depth+1,dump_flags,contents)
        dump_flags[cfg]=True

    def DumpFlattenConfigs(self,cfg):
        contents=list()
        contents.append('===DumpFlattenConfigs===')
        (cvspath,codetag,depstag,revision,athead)=(cfg.CVSPath(),
                                   cfg.CodeTag(),
                                   cfg.DepsTag(),
                                   cfg.Revision(),
                                   cfg.AtHEAD())
        contents.append('%s@%s'%(cvspath,codetag))
        if(cfg.DisableBuild()==True):
            contents.append('[Disable Build]')
            return contents
        key=self._env.SCMSystem().GetDepKey(cvspath,codetag,depstag,revision,athead) 
        for subcfg in self._flatten_compile_deps_cache[key]:
            contents.append('    %s@%s'%(subcfg.CVSPath(),subcfg.CodeTag()))
        return contents

    def DumpMapConfigs(self):
        contents=list()
        contents.append('===DumpMapConfigs===')
        for cvspath in self._map_direct_configs.keys():
            contents.append('%s:[%s]'%(cvspath,' '.join(self._map_direct_configs[cvspath])))
        return contents

    def DumpSortedConfigs(self,cfg):
        contents=list()
        contents.append('===DumpSortedConfigs===')
        (cvspath,codetag,depstag)=(cfg.CVSPath(),
                                   cfg.CodeTag(),
                                   cfg.DepsTag())
        contents.append('%s@%s'%(cvspath,codetag))
        for subcfg in self._sorted_configs:
            contents.append('    %s@%s'%(subcfg.CVSPath(),subcfg.CodeTag()))
        return contents

