#!/usr/bin/env python
#coding:gbk
#Copyright (c) Baidu.com, Inc. All Rights Reserved 
#author:zhangyan04(@baidu.com)

import os

import Function
import SyntaxTag

"""
为什么这里变量叫做ccj.是因为原来
类的设计里面都加上了前缀CM,所以CJson->CCJ
"""

class CJson(object):
    def __init__(self):
        pass    
    
    def InitFromArgs(self,
                     cvspath,#cvspath.
                     codetag,#代码tag.
                     revision,#修订号.
                     depstag,#依赖tag.
                     nullobjs,#是否为空对象.
                     objects,#绑定对象.
                     buildcmd,#编译命令
                     disbuild_flag,#是否编译
                     status):#版本状态
        self._cvspath=cvspath
        self._codetag=codetag
        self._revision=revision
        self._depstag=depstag
        self._nullobjs=nullobjs
        self._objects=objects
        self._parent=None
        self._depth=1
        self._buildcmd=buildcmd
        self._disable_build_flag=disbuild_flag
        self._status=status
        self._importdirs=list()
            
    def InitFromJson(self,json):
        self._cvspath=json['cvspath']
        self._codetag=json['codetag']
        self._revision=json['revision']
        self._depstag=json['depstag']
        self._nullobjs=json['nullobjs']
        self._objects=json['objects']
        self._buildcmd=json['buildcmd']
        self._disable_build_flag=json['disbuild_flag']
        self._status=json['status']
        self._importdirs=list()
        if('parent' in json):
            ccj=CJson()
            ccj.InitFromJson(json['parent'])
            self._parent=ccj
        else:
            self._parent=None
        self._depth=1
        if(self._parent):
            self._depth=self._parent.Depth()+1
            
    def MergeCCJ(self,ccj):
        self._objects.extend(ccj.Objects())
        self._objects=Function.Unique(self._objects)
        if(ccj.DisableBuild()==False):
            self._disable_build_flag=False

    def AppendParent(self,parent):
        if(self._parent):
            self._parent.AppendParent(parent)
        else:
            self._parent=parent
        self._depth=self._parent.Depth()+1
        
    def SerializeToJson(self):
        """序列化成为Json格式."""
        json={}
        json['cvspath']=self._cvspath
        json['codetag']=self._codetag
        json['revision']=self._revision
        json['depstag']=self._depstag
        json['nullobjs']=self._nullobjs
        json['objects']=self._objects
        json['buildcmd']=self._buildcmd
        json['disbuild_flag']=self._disable_build_flag
        json['status']=self._status
        if(self._parent):
            json['parent']=self._parent.SerializeToJson()
        return json

    def SerializeToText(self,level,forshort=False):
        """序列化成为text格式.
        会把parent信息打印出来"""
        prefix_tag='\t'*level
        
        parent_tag=''
        if(self._parent):
            parent_tag='\n%s'%(self._parent.SerializeToText(level+1,forshort))

        revision_tag=''
        if(self._revision):
            revision_tag='[revision:%s]'%(self._revision)

        objects_tag=''
        if(self._objects):
            objects_tag='[objects:%s]'%(self._objects)

        buildcmd_tag=''
        if(self._buildcmd):
            buildcmd_tag='[buildcmd:%s]'%(self._buildcmd)

        disbuild_tag=''
        if(self._disable_build_flag):
            disbuild_tag='[disbuild:%s]'%(self._disable_build_flag)

        status_tag=''
        if(self._status):
            status_tag ='[status:%s]'%(self._status)

        importdir_tag=''
        for i_dir in self._importdirs:
            importdir_tag='\n%s\t<>[%s]'%(prefix_tag,i_dir)

        cvspath_tag=''
        if(self._cvspath):
            cvspath_tag='[cvspath:%s]'%(self._cvspath)

        codetag_tag=''
        if(self._codetag):
            codetag_tag='[codetag:%s]'%(self._codetag)

        depstag_tag=''
        if(self._depstag):
            depstag_tag='[depstag:%s]'%(self._depstag)
                 
        if(forshort==False):
            s="%(prefix_tag)s%(cvspath_tag)s%(codetag_tag)s"%(locals())
            s+="%(revision_tag)s%(status_tag)s%(depstag_tag)s%(objects_tag)s%(buildcmd_tag)s%(disbuild_tag)s%(importdir_tag)s"%(locals())
        else:
            s="%(prefix_tag)s%(cvspath_tag)s%(codetag_tag)s"%(locals())
            s+="%(revision_tag)s%(status_tag)s%(objects_tag)s%(importdir_tag)s"%(locals())
        s+="%(parent_tag)s"%(locals())
        return s

    def __str__(self):
        return '%s'%(self.SerializeToText(0))
    def __repr__(self):
        return '%s'%(self.SerializeToText(0))
    def CVSPath(self):
        return self._cvspath
    def CodeTag(self):
        return self._codetag
    def SetCodeTag(self,v):
        self._codetag=v
    def Revision(self):
        return self._revision
    def DepsTag(self):
        return self._depstag
    def NullObjects(self):
        return self._nullobjs
    def SetNullObjects(self,nullobjs):
        self._nullobjs=nullobjs
    def Objects(self):
        return self._objects
    def SetObjects(self,objects):
        self._objects=objects
    def BuildCmd(self):
        return self._buildcmd
    def SetBuildCmd(self,buildcmd):
        self._buildcmd=buildcmd
    def DisableBuild(self):
        return self._disable_build_flag
    def SetDisableBuild(self,disable_build_flag):
        self._disable_build_flag=disable_build_flag
    def Status(self):
        return self._status
    def AppendImportDir(self,v):
        if(not v in self._importdirs):
            self._importdirs.append(v)
    def Parent(self):
        return self._parent
    def Depth(self):
        return self._depth
    def SetDepth(self,v):
        self._depth=v
    def __eq__(self,v):
        return (self._cvspath==v._cvspath and
                self._codetag==v._codetag and
                self._revision==v._revision and
                self._depstag==v._depstag and
                self._nullobjs==v._nullobjs and
                self._objects==v._objects)
    def __ne__(self,v):
        return not self.__eq__(v)


class Config(object):
    def __init__(self):
        pass
    
    def InitFromArgs(self,
                     cvspath,#cvspath.
                     codetag,#代码tag.
                     revision,#修订号.
                     depstag,#依赖tag.
                     args,
                     buildcmd,
                     status,
                     athead,
                     env):
        self._cvspath=cvspath
        self._codetag=codetag
        self._revision=revision
        self._depstag=depstag
        self._args=args
        self._env=env 
        self._log=env.LogSystem()
        self._scm=env.SCMSystem()
        self._depends=[] #自己所持有的Depend对象.
        self._disable_build_flag=False
        self._buildcmd=buildcmd
        self._status=status
        self._stable_revision=False
        self._athead=athead
 
        #检测Objects.
        flag=False

        objects=[]
        for arg in self._args:
            if(isinstance(arg,SyntaxTag.TagLibraries)):
                flag=True
                objects.extend(arg.V())
            elif(isinstance(arg,SyntaxTag.TagDisableBuild)):
                self._disable_build_flag=arg.V()
            elif(isinstance(arg,SyntaxTag.TagBuildCmd)):
                self._log.LogWarning(
                       "Be aware! To specify building %s with '%s'"%(self._cvspath,arg.V()))
                self._buildcmd=arg.V()
        objects=Function.Unique(objects)
        self._nullobjs=False
        if(flag and not objects):
            self._nullobjs=True
        self._objects=objects
        
        #构造自身的CJson表示.
        ccj=CJson()
        ccj.InitFromArgs(cvspath,
                        codetag,
                        revision,
                        depstag,
                        self._nullobjs,
                        self._objects,
                        self._buildcmd,
                        self._disable_build_flag,
                        self._status)
        self._ccj=ccj

        self._direct_deps=[]

    def CVSPath(self):
        return self._cvspath
    def CodeTag(self):
        return self._codetag
    def SetCodeTag(self,codetag):
        self._codetag=codetag
        self._ccj._codetag=codetag
    def Revision(self):
        return self._revision
    def AtHEAD(self):
        return self._athead
    def DepsTag(self):
        return self._depstag    
    def SetDepsTag(self,depstag):
        self._depstag=depstag
        self._ccj._depstag=depstag
    def BuildCmd(self):
        return self._buildcmd
    def SetBuildCmdIfNull(self,k):
        if(not self._buildcmd):
            self._buildcmd=k
    def Status(self):
        return self._status
    def SetStatus(self,k):
        self._status=k
    def DisableBuild(self):
        return self._disable_build_flag
    def BasePath(self,env):
        return os.path.join(env.WorkRoot(),
                            self._cvspath)
    def CCJ(self):
        return self._ccj
    def Args(self):
        return self._args
    def Objects(self):
        return self._objects
    def Env(self):
        return self._env
    def StableRevision(self):
        return self._stable_revision
    def MarkStableRevision(self,k):
        self._stable_revision=k
    def ParseArgs(self,args):
        self._args=args
        #检测Objects.
        flag=False

        objects=[]
        for arg in self._args:
            if(isinstance(arg,SyntaxTag.TagLibraries)):
                flag=True
                objects.extend(arg.V())
            elif(isinstance(arg,SyntaxTag.TagDisableBuild)):
                self._disable_build_flag=arg.V()
            elif(isinstance(arg,SyntaxTag.TagBuildCmd)):
                self._log.LogWarning(
                       "Be aware! To specify building %s with '%s'"%(self._cvspath,arg.V()))
                self._buildcmd=arg.V()
        objects=Function.Unique(objects)
        self._nullobjs=False
        if(flag and not objects):
            self._nullobjs=True
        self._objects=objects

        self._ccj.SetNullObjects(self._nullobjs)
        self._ccj.SetObjects(self._objects)
        self._ccj.SetBuildCmd(self._buildcmd)
        self._ccj.SetDisableBuild(self._disable_build_flag)

    def MergeCfg(self,cfg):
        self._objects.extend(cfg.Objects())
        self._objects=Function.Unique(self._objects)
        if(cfg.DisableBuild()==False):
            self._disable_build_flag=False
        self._ccj.MergeCCJ(cfg._ccj)

    def AppendParent(self,parent):
        if(parent and parent.CCJ()):
            self._ccj.AppendParent(parent.CCJ())

    def AppendDirectDep(self,cfg):
        self._direct_deps.append(cfg)

    def AppendImportDir(self,v):
        self._ccj.AppendImportDir(v)

    def DetectObjects(self,env):
        basepath=os.path.normpath(
            os.path.join(env.WorkRoot(),
                         self._cvspath))
        func_name="[Action:DetectObjects][basepath:%s]"%(basepath)
        objects=self._objects        
        #如果没有指定为空,但是object为空.
        #但是需要自己自己去侦测目录下面的库文件.
        if(not self._nullobjs and
           not self._objects and
           os.path.exists(basepath)):
            objects=self._scm.DetectLocalObjects(basepath)
        if(not objects):
            #NOTICE(zhangyan04)如果没有的话,返回空列表.但是告诉用户我们没有找到.
            self._log.LogNotice('%s[objects:(null)]'%(func_name))
        return objects
    
    def CreateDepends(self,env):
        #这个过程只是运行一次.
        #初始的时候我们只是确保不断地添加Config对象和Depend对象.
        #但是并不做任何检测活动.求得Config对象的闭包之后,然后再检查Depend对象
        #这样就不会出现计算顺序问题了.
        objects=self.DetectObjects(env)
        for obj in objects:
            self._depends.append(
                env.CreateDepend(self._cvspath,
                                       os.path.normpath(obj),
                                       self._args))
        #如果没有任何Libraries的话,我们依然需要添加一个Depend对象
        #因为事实上外部可能并不意外任何Depend对象,但是却依赖了其他内容
        #包括头文件等,还需要提供-I参数等信息.tricky way,huh?
        if(not objects):
            self._depends.append(
                env.CreateDepend(self._cvspath,
                                       '',
                                       self._args))
    def Depends(self):
        return self._depends    
    def SerializeToText(self,level,forshort=False):
        return self._ccj.SerializeToText(level,forshort)
    def SerializeToJson(self):
        return self._ccj.SerializeToJson()
    def Depth(self):
        return self._ccj.Depth()
    def SetDepth(self,v):
        self._ccj.SetDepth(v)
    def __str__(self):
        return '%s'%(self.SerializeToText(0))
    def __repr__(self):
        return '%s'%(self.SerializeToText(0))
        
class Depend(object):
    def __init__(self,
                 cvspath,
                 object,
                 args,
                 env):
        self._cvspath=cvspath
        self._object=os.path.normpath(object)
        self._args=args
        self._env=env        
        self._scm=env.SCMSystem()
        self._incpaths=[] #Depend对象使用的头文件路径.
        self._depends=[] #自身依赖了什么Depend对象.
    
    def CVSPath(self):
        return self._cvspath    
    def BasePath(self,env):
        return os.path.normpath(
            os.path.join(env.WorkRoot(),
                         self._cvspath))
    def Object(self):
        return self._object    
    def Depends(self):
        return self._depends
    def IncludePaths(self):
        return self._incpaths    
    def __eq__(self,v):
        return (self._cvspath==v._cvspath and
                self._object==v._object)

    def DetectIncludePaths(self):
        """检测Depend对象所使用的头文件"""
        flag=False
        incpaths=[]    
        for arg in self._args:
            if(isinstance(arg,SyntaxTag.TagIncludePaths)):
                flag=True
                incpaths.extend(arg.V())
        if(not flag):
            incpaths=['.',
                      './include',
                      './output',
                      './output/include']
            incpaths=map(lambda x:os.path.normpath(x),
                         incpaths)
        self._incpaths=incpaths
    
#     def DetectDepends(self):
#         """检测Depend对象所依赖的Depend对象"""
#         cfg=self._env.QueryConfig(self._cvspath)
#         deps=self._scm.GetCompileDeps(
#             self._cvspath,
#             cfg.CodeTag(),
#             cfg.DepsTag())
#         depends=[]
#         for dep in deps:
#             config=self._env.QueryConfig(dep.CVSPath())
#             depends.extend(config.Depends())
#         depends=Function.Unique(depends,
#                                 lambda x:'%s:%s'%(x._cvspath,x._object))
#         self._depends=depends
        
    def Detect(self):
        self.DetectIncludePaths()
        #self.DetectDepends()

def duplicate(cfg,env):
    dup=Config()
    dup.InitFromArgs(cfg._cvspath,
                     cfg._codetag,
                     cfg._revision,
                     cfg._depstag,
                     cfg._args,
                     cfg._buildcmd,
                     cfg._status,
                     cfg._athead,
                     env)
    dup.MarkStableRevision(cfg.StableRevision())
    return dup

class ConfigASH(object):
    def __init__(self,
                 cvspath,
                 codetag,
                 revision):
        self._cvspath=cvspath
        self._codetag=codetag
        self._revision=revision

    def CVSPath(self):
        return self._cvspath

    def CodeTag(self):
        return self._codetag

    def Revision(self):
        return self._revision

