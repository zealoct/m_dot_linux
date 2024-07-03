#!/usr/bin/env python
#coding:gbk
#Copyright (c) Baidu.com, Inc. All Rights Reserved 
#author:zhangyan04(@baidu.com)

import string
import urllib2
import os
import re
import socket

import Config
import Function
import CodeSystem
import DepAlgorithm

network_line_cache={}
devtag_url_cache={} #svn url of developing four-version-tag
compile_deps_cache=dict()
compile_args_cache=dict()

UNCERTAIN=-1
ISNEWER=0
MISSNEWER=1

warn_config_base_once=False

class BaiduSCMSystem(object):
    def __init__(self,env):
        self._env=env
        self._log=env.LogSystem()
        self._BRANCH_TAG=['branch','research']
        self._TRUNK_TAG='trunk' #trunk标记.
        self._COMAKE_TAG='comake' #comake标记.
        self._BASE_TAG='base'#base标记.
        self._CI_TAG='ci' #ci标记.
        self._NULL_TAG='null' #null标记
        self._PKG_TAG='pkg' #pkg标记.
        #self._network_line_cache={}
        self._formal_tag_cache={}
        self._local_libraries={}
        self._cvspath_tables=(('lib2',64,'lib2-64'),
                              ('third',64,'third-64'),
                              ('lib2-64',32,'lib2'),
                              ('third-64',32,'third'))
        self._network_line_diskcache_dir=os.path.join(
            os.environ['HOME'],'.COMAKE.CACHE')
        self._devtag_url_diskcache_dir=os.path.join(
            os.environ['HOME'],'.COMAKE.CACHE/tag_urls')

    def IsTagBranch(self,tag):
        for br_tag in self._BRANCH_TAG:
            tmp=string.upper(br_tag)
            if(tag.find(tmp)!=-1):
                return True
        return False
    def IsTagTrunk(self,tag):
        return string.lower(tag)==self._TRUNK_TAG
    def IsTagCOMAKE(self,tag):
        return string.lower(tag)==self._COMAKE_TAG
    def IsTagBase(self,tag):
        return string.lower(tag)==self._BASE_TAG
    def IsTagNull(self,tag):
        return string.lower(tag)==self._NULL_TAG
    def IsTagCI(self,tag):
        return string.lower(tag)==self._CI_TAG
    def IsTagPkg(self,tag):
        return string.lower(tag)==self._PKG_TAG
    def IsCodeTagTrivial(self,tag):
        return (not self.IsTagTrunk(tag) and
                not self.IsTagBranch(tag) and
                not self.IsTagBase(tag) and
                not self.IsTagCI(tag))    
    def IsDepsTagTrivial(self,tag):
        return (not self.IsTagCOMAKE(tag) and
                not self.IsTagNull(tag) and
                not self.IsTagBase(tag))
    
    def Tag2Number(self,tag):
        func_name="[Action:Tag2Number]"
        retag=re.compile(r'\d+-\d+-\d+-\d+')        
        ps=string.split(tag,'_')
        version=None
        for p in ps:
            if(retag.match(p)):
                version=map(lambda x:int(x),string.split(p,'-'))
                break
        if(not version):
            self._log.LogFatal('%s[INVALID:%s]'%(func_name,tag))
        base=1000
        number=0
        for i in version:
            number=number*base+i
        return number

    def _GetFormalDepsTag(self,cvspath,s):
        if(self.IsTagCOMAKE(s)):
            depstag=s
        elif(self.IsTagBase(s)):
            depstag=self._GetFormalTag(cvspath,'')[1]
        elif(self.IsTagNull(s)):
            depstag=s
        else:
            depstag=self._GetFormalTag(cvspath,s)[1]
        return depstag

    def _GetFormalCodeTag(self,cvspath,s):
        buildcmd=''
        status=''
        if(self.IsTagTrunk(s)):
            codetag=self._TRUNK_TAG
        elif(self.IsTagBranch(s)):
            codetag=s
        elif(self.IsTagBase(s)):
            dep=self._GetFormalTag(cvspath,'')
            (codetag,buildcmd,status)=(dep[1],dep[2],dep[3])
        elif(self.IsTagCI(s)):
            codetag=self._TRUNK_TAG
        elif(self.IsTagPkg(s)):
            if(not self._env.IsConfigsPackaged(cvspath)):
                self._log.LogFatal('%s not found in config package'%cvspath)
            codetag=self._env.QueryConfigsPackaged(cvspath).CodeTag()
        else:
            dep=self._GetFormalTag(cvspath,s)
            (codetag,buildcmd,status)=(dep[1],dep[2],dep[3])
        return (codetag,buildcmd,status)

    def _NonExistingTag2Url(self,dep):
        func_name="[Action:_NonExistingTag2Url]"
        (cvspath,codetag,status,depstag)=(dep[0],dep[1],dep[3],dep[4])
        if(status=='new' or status=='build'):
            status=self._env.CodeSystem().IsTagExists(cvspath,codetag)
            if(status==CodeSystem.NO_EXISTS):
                svn_url=self.GetSvnUrlByTag(cvspath,codetag)
                msg="%sCONFIGS('%s@%s') >> CONFIGS('%s@%s@%s')"%(func_name,cvspath,codetag,cvspath,svn_url,depstag)
                self._log.LogDebug(msg,1)
                return (dep[0],svn_url,dep[2],dep[3],dep[4])
        return dep

    def _AnalyzeDepsFromLine(self,line,pickfirst=False):
        """对SCM传回来的一行进行那个分析,这个作为一个单独例程
        非常具有通用性"""
        #使用{$@....@$}来进行拆分.里面使用|@|来进行分割..
        #然后依赖的模块是0,4位版本1,tag是2.
        begin=0
        end=0
        deps=[]
        while(True):
            begin=string.find(line[end:],"{$@")
            if(begin==-1):
                break
            begin+=end
            begin+=len("{$@")
            end=string.find(line[begin:],"@$}")
            if(end==-1):
                break
            end+=begin
            ps=string.split(line[begin:end],'|@|')
            deps.append((ps[0],ps[2],ps[3],ps[4],ps[2]))
            if(pickfirst):
                break
            end+=len("@$}")
        for i in range(1,len(deps)):
            deps[i]=self._NonExistingTag2Url(deps[i])
        return deps
    
    def _IsReleaseStatus(self,status):
        return (status=='released'
                or status=='releasing'
                or status=='pre-release')

    def _IsBuildOKStatus(self,status):
        '''TODO: 'build' consists of build-failure and build-ok, need to tell it'''
        return not (status=='new' or status=='build')

    def _CompareTags(self,oldtag,newtag):
        number1=self.Tag2Number(oldtag)
        number2=self.Tag2Number(newtag)
        max_number=max(number1,number2)
        if(max_number != number1):
            return MISSNEWER
        return ISNEWER

    def CompareConfigs(self,oldcfg,newcfg):
        oldtag=oldcfg.CodeTag()
        newtag=newcfg.CodeTag()
        if(oldtag==newtag):
            return ISNEWER
        oldstatus=oldcfg.Status()
        newstatus=newcfg.Status()
        if(self._IsReleaseStatus(oldstatus)):
            if(self._IsReleaseStatus(newstatus)):
                return self._CompareTags(oldtag,newtag)
            else:
                return MISSNEWER
        else:
            if(self._IsReleaseStatus(newstatus)):
                return ISNEWER
            else:
                return UNCERTAIN

    def IsNewer(self,status):
        return status==ISNEWER
    def MissNewer(self,status):
        return status==MISSNEWER
    def UncertainNewer(self,status):
        return status==UNCERTAIN

    def _NeedDiskCache(self,line):
        """仅在本地缓存平台上编译通过的版本信息"""
        try:
            deps=self._AnalyzeDepsFromLine(line,pickfirst=True)
            status=deps[0][3]
            if(not self._IsBuildOKStatus(status)):
                return False
        except:
            return False
        return True

    def GetSvnUrlByTag(self,cvspath,tag):
        func_name="[Action:GetSvnUrlByTag][cvspath:%s][tag:%s]"%(
            cvspath,
            tag)
        key='%s@%s'%(cvspath,tag)
        if(key in devtag_url_cache):
            return devtag_url_cache[key]
        cache_file=os.path.join(self._devtag_url_diskcache_dir,
                                key.replace('/','.'))
        if(tag and os.path.exists(cache_file)):
            line=open(cache_file).read()
            devtag_url_cache[key]=line
            return line

        SERVICE_URL='http://scm.baidu.com/http/queryBranches.action'
        req_url='%s?cvspath=%s&version=%s'%(SERVICE_URL,cvspath,tag)        
        self._log.LogDebug("%s[req_url:%s]"%(func_name,req_url),1)
        URL_TIMEOUT=60
        try:
            socket.setdefaulttimeout(URL_TIMEOUT)
            data=urllib2.urlopen(req_url).read()
        except urllib2.URLError,e:            
            self._log.LogFatal("%s:[urllib2.URLError:%s]"%(func_name,e))
        if('"errno":' in data):
            try:
                data=data.decode('utf-8').encode('gbk')
            except:
                pass
            self._log.LogDebug('%s[return error: "%s"]'%(func_name,data),1)
            devtag_url_cache[key]=tag
            return tag

        try:
            if(not os.path.exists(self._devtag_url_diskcache_dir)):
                os.makedirs(self._devtag_url_diskcache_dir)
            open(cache_file,'w').write(data)
        except Exception,e:
            self._log.LogDebug("%s:[cache_file:%s][Exception:%s]"%(
                    func_name,cache_file,e))
        devtag_url_cache[key]=data
        return data

    def _NetworkGetCompileDepsLine(self,cvspath,tag):
        """从网络读取依赖编译依赖"""
        #we can cache it to local file.
        func_name="[Action:_NetworkGetCompileDepsLine][cvspath:%s][tag:%s]"%(
            cvspath,
            tag)
        #有内存层cache和磁盘层cache.
        key='%s@%s'%(cvspath,tag)
        if(key in network_line_cache):
            return network_line_cache[key]
        cache_file=os.path.join(self._network_line_diskcache_dir,
                                key.replace('/','.'))
        #NOTICE(zhangyan04):
        #对于取基线的话,不能够使用.
        if((self._env.ReCache()==False) and tag and os.path.exists(cache_file)):
            line=open(cache_file).read()
            if(self._NeedDiskCache(line)):
                network_line_cache[key]=line
                return line
            else:
                #remove the previously cached files.
                os.remove(cache_file)
 
        #从网络获取依赖.
        SERVICE_URL='http://scm.baidu.com/http/getCompilerDep.action'
        req_url='%s?cvspath=%s&version=%s'%(SERVICE_URL,cvspath,tag)        
        self._log.LogDebug("%s[req_url:%s]"%(func_name,req_url),2)
        URL_TIMEOUT=60
        try:
            socket.setdefaulttimeout(URL_TIMEOUT)
            data=urllib2.urlopen(req_url).read()
        except urllib2.URLError,e:            
            self._log.LogFatal("%s:[urllib2.URLError:%s]"%(func_name,e))
        line=''.join(string.split(data,'\n'))
        #如果是''的tag,那么直接存入内存层cache.
        if(not tag):
            network_line_cache[key]=line
            return line
        
        #如果状态是开发中的话，也直接存入内存层cache
        if(not self._NeedDiskCache(line)):
            network_line_cache[key]=line
            return line

        #如果非''的tag,那么可以保存与磁盘cache.
        try:
            if(not os.path.exists(self._network_line_diskcache_dir)):
                os.mkdir(self._network_line_diskcache_dir)
            open(cache_file,'w').write(line)
        except Exception,e:
            self._log.LogDebug("%s:[cache_file:%s][Exception:%s]"%(
                    func_name,cache_file,e))
        network_line_cache[key]=line
        return line

    def _GetFormalTag(self,cvspath,tag):
        """得到一个规范的TAG,比如ub_1-0-0-0_PD_BL"""
        func_name="[Action:_GetFormalTag][cvspath:%s][tag:%s]"%(cvspath,
                                                                tag)
        key='%s@%s'%(cvspath,tag)
        if(key in self._formal_tag_cache):
            return self._formal_tag_cache[key]
        dep=()
        try:
            line=self._NetworkGetCompileDepsLine(cvspath,tag)
            deps=self._AnalyzeDepsFromLine(line)
            if(deps):
                dep=deps[0]
        except Exception,e:
            self._log.LogWarning("%s[Exception:%s]"%(func_name,e))
        if(not dep):
            if(tag and not tag[0].isdigit()):
            #如果已经是ub_1-0-0-0_PD_BL的话.
            #那么直接使用
                dep=(cvspath,tag,'','','')
            else:
                dep=(cvspath,self._NULL_TAG,'','','')
        self._formal_tag_cache[key]=dep
        return dep
    
    def ParseConfig(self,s):
        func_name="[Action:ParseConfig]"
        #1.CodeTag,表示实际使用代码所使用的Tag.
        #2.DepsTag,表示在查找编译依赖的时候,所使用的Tag.
        ps=string.split(s,'@')
        #TODO(zhangyan04):这个地方可以做更完整教研.
        #如果存在3个部分的话,那么第一个部分是cvspath,
        #第二部分是codetag
        #第三部分是depstag
        if(not len(ps) in (1,2,3) or
           (len(ps)==2 and (not ps[1])) or
           (len(ps)==3 and ((not ps[1]) or (not ps[2]))) or
           not ps[0]):
            self._log.LogFatal("%s[INVALID:%s]"%(func_name,s))    
        #这里帮助用户纠正错误.
        #很多用户会以/开头,这里我们需要纠正.
        cvspath=ps[0]
        if(cvspath[0]=='/'):
            cvspath=cvspath[1:]
        if(cvspath[-1]=='/'):
            cvspath=cvspath[:-1]
        #关于这个部分的处理
        #可以参考comake2.org里面的说明.
        if(len(ps)==1):
            global warn_config_base_once
            if(not warn_config_base_once):
                self._log.LogWarning("""in %s/COMAKE:CONFIGS('%s'): deprecated, use CONFIGS('%s@base') instead.
No more warnings for similar cases"""%(self._env.CVSPath(),s,s))
                warn_config_base_once=True
            codetag=''
            revision=''
            depstag=''
        else:
            #需要把ps[1]部分拆解开.
            #这个部分包含了tag和revision.
            xs=string.split(ps[1],':',maxsplit=1)
            if(len(xs)==2):
                (ps[1],revision)=xs
            else:
                revision=''
            codetag=ps[1]
            if(len(ps)==3):
                depstag=ps[2]
            else:
                #默认使用基线.
                depstag=''
                #如果是CI模式的话.
                if(self.IsTagCI(codetag)):
                    depstag=self._COMAKE_TAG
                #如果是tag的话
                if(self.IsCodeTagTrivial(codetag)):
                    depstag=codetag
        #获取codetag和depstag
        (codetag,buildcmd,status)=self._GetFormalCodeTag(cvspath,codetag)
        depstag=self._GetFormalDepsTag(cvspath,depstag)
        #调整cvspath.
        ps=string.split(cvspath,'/')
        for (o,b,n) in self._cvspath_tables:
            if(ps[0]==o and 
               self._env.Bit()==b):
                ps[0]=n
        cvspath='/'.join(ps)

        return (cvspath,codetag,revision,depstag,buildcmd,status)

    def GetDepKey(self,cvspath,codetag,depstag,revision,athead):
        bit=self._env.Bit()
        if(self.IsTagCOMAKE(depstag)):
            if(athead==True):
                key='%s@%s@%d'%(cvspath,codetag,bit)
            else:
                key='%s@%s:%s@%d'%(cvspath,codetag,revision,bit)
        else:
            key='%s@%s@%d'%(cvspath,depstag,bit)
        return key

    def SetCompileDepsCache(self,key,dep_list):
        compile_deps_cache[key]=dep_list

    def SetCompileArgsCache(self,key,arg_dict):
        compile_args_cache[key]=arg_dict

    def GetCompileDepsAndArgs(self,cvspath,codetag,depstag,revision,athead):
        """编译依赖内容.格式以CMConfigJson来表示.
        这样可以很容易地从构造出Config对象出来"""    
        func_name="[Action:GetCompileDeps][cvspath:%s][codetag:%s][depstag:%s][revision:%s][athead:%s]"%(
            cvspath,
            codetag,
            depstag,
            revision,
            athead)
        args=dict()
        #如果不去操作任何依赖的话.
        if(self.IsTagNull(depstag)):
            return ([],args)
        
        #对于COMAKE的depstag的话,我们关心codetag.
        #而对于非COMAKE的话,我们关心depstag.
        #使用缓存.
        key=self.GetDepKey(cvspath,codetag,depstag,revision,athead)
        if(key in compile_deps_cache):
            return (compile_deps_cache[key],compile_args_cache[key])

        if(self.IsTagCOMAKE(depstag)):
            #We can't cache it.
            basepath=os.path.join(self._env.WorkRoot(),cvspath)
            defaultcomake = os.path.join(basepath,"COMAKE")
            comakefile = defaultcomake
            if(self._env.DoingUpdate() or self._env.DumpCfgs()):
                if cvspath==self._env.CVSPath() or cvspath.startswith('%s/'%(self._env.CVSPath())):
                    pass
                else:
                    comakefile = "/tmp/%s.%d.%d.COMAKE"%(os.path.abspath(basepath).replace("/","."), os.getpid(), os.getuid())
                    getcomakecmd = self._env.CodeSystem().ExportCOMAKECommand(cvspath, codetag, revision, comakefile)
                    if not os.path.exists(basepath):
                        getcomakecmd = "mkdir -p %s &&"%basepath + getcomakecmd
                    (status,_,_) = self._env.CodeSystem().ConnectSvn(getcomakecmd, no_verify=True, func_name="[Action:GetCOMAKE]")
                    if status:
                        self._log.LogFatal('%s[basepath:%s][COMAKE:!exists]'%(func_name,
                                                                              basepath))
            if(not os.path.exists(comakefile)):
                self._log.LogFatal('%s[basepath:%s][COMAKE:%s !exists]'%(func_name,
                                                                         basepath,
                                                                         comakefile))
            (configs,args,_)=self._env.GetConfigsFromCOMAKE(basepath, comakefile)
            if comakefile != defaultcomake:
                os.system("rm -rf %s"%comakefile)
            self._log.LogDebug('%s[deps:%s]'%(func_name,configs),2)
        else:
            try:
                #网络交互查询.
                deps=self._AnalyzeDepsFromLine(
                    self._NetworkGetCompileDepsLine(cvspath,depstag))
                try:
                    if(deps and self._env.CVSPath() and cvspath != self._env.CVSPath()):
                        if(self._env.NewDA()==True):
                            cfg=self._env.DepSystem().QueryConfig(cvspath,codetag,'')
                        else:
                            cfg=self._env.QueryConfig(cvspath)
                        cfg.SetBuildCmdIfNull(deps[0][2])
                        cfg.SetStatus(deps[0][3])
                except:
                    self._log.LogWarning("%s[QueryConfig failed: %s]"%(func_name,cvspath))
                configs=[]
                for dep in deps[1:]:
                    #过滤掉不合适的模块.
                    flag=True
                    ps=string.split(dep[0],'/')
                    for (o,b,n) in self._cvspath_tables: 
                        if(self._env.Bit()==b and
                           ps[0]==o):
                            flag=False
                            break
                    if(not flag):
                        continue
                    #TODO: scmpf needs tell if the dep needs build (reguarding to disbuild_flag)
                    cfg=self._env.DepSystem().GetOrInitConfigFromArgs(dep[0],#cvspath
                                     dep[1],#codetag
                                     '',#revision
                                     dep[4],#depstag
                                     [],#args
                                     dep[2],#buildcmd.
                                     dep[3],#status
                                     self._env)
                    configs.append(cfg)
                self._log.LogDebug("%s[deps:%s]"%(func_name,configs),2)
            except Exception,e:
                self._log.LogFatal("%s[Exception:%s]"%(func_name,e))
        if(not self.IsTagTrunk(codetag) and not self.IsTagBranch(codetag)):
            self._MarkStableRevision(configs) 
        self.SetCompileDepsCache(key,configs)
        self.SetCompileArgsCache(key,args)
        return (configs,args)

    def GetCompileDeps(self,cvspath,codetag,depstag,revision='',athead=True):
        return self.GetCompileDepsAndArgs(cvspath,codetag,depstag,revision,athead)[0]

    def _MarkStableRevision(self,configs):
        for cfg in configs:
            if(self.IsTagTrunk(cfg.CodeTag()) or self.IsTagBranch(cfg.CodeTag())):
                cfg.MarkStableRevision(True)

    def DetectLocalObjects(self,path):
        return self.DetectLocalLibraries(path)
    
    def DetectLocalLibraries(self,path):
        """检查本地目录下面的.a文件"""
        #func_name='[Action:DetectLocalLibraries]'
        if(path in self._local_libraries):
            return self._local_libraries[path]
        
        #首先检查目录下面是否存在.
        #搜索路径也是固定的.
        cwd=os.getcwd()
        os.chdir(path)
        exts=('.a',)
        libs=Function.FindFilesExts('.',False,exts)
        if(os.path.exists('./output')):
            libs+=Function.FindFilesExts('./output',True,exts)
        if(os.path.exists('./lib')):
            libs+=Function.FindFilesExts('./lib',True,exts)
        libs=Function.Unique(libs,lambda x:
                                 os.path.basename(x))
        os.chdir(cwd)

        #NOTICE(zhangayan04):
        #如果没有找到libs
        #并且目录下面存在COMAKE文件.
        #那么需要去分析COMAKE文件来发现.
        if(not libs and 
           os.path.exists(os.path.join(path,'COMAKE'))):
            libs=self._env.GetCurrent().GetStaticLibraryNamesFromCOMAKE(path)
        self._local_libraries[path]=libs
        return libs

