#!/usr/bin/env python
#coding:gbk
#Copyright (c) Baidu.com, Inc. All Rights Reserved 
#author:zhangyan04(@baidu.com)

import os
import SyntaxTag
import Function

warn_linkdeps_once=False

class Target(object):
    TYPE='target'
    def __init__(self,name,args,env):
        self._name=os.path.normpath(name)
        self._target=''
        self._env=env
        self._args=args

        self._make_lines=[] #make命令
        self._make_clean_lines=[] #make clean命令
        self._clean_files=[] #删除文件列表
        self._phony_mode=False #虚拟target.
        self._prefixes=[] #依赖前缀.
        self._sources=[] #依赖源文件.
        self._depends=[] #依赖Depend对象.
        self._header_files=[] #发布的头文件.
        self._line_delim=' \\\n  '
        self._space_delim=' '
        
        self._depends_libs=[] 
        self._depends_libs_s=''
        self._sources_infiles=[]
        self._sources_outfiles=[]
        
    def Name(self):
        return self._name
    def BaseName(self):
        return os.path.basename(self._name)
    def Env(self):
        return self._env
    def Args(self):
        return self._args
    def Target(self):
        return self._target
    def MakeLines(self):
        return self._make_lines
    def MakeCleanLines(self):
        return self._make_clean_lines
    def CleanFiles(self):
        return self._clean_files
    def PhonyMode(self):
        return self._phony_mode
    def Prefixes(self):
        return self._prefixes
    def Sources(self):
        return self._sources
    def SourcesInFiles(self):
        return self._sources_infiles
    def SourcesOutFiles(self):
        return self._sources_outfiles
    def HeaderFiles(self):
        return self._header_files    
    def Depends(self):
        return self._depends
    def DependsLibraries(self):
        return self._depends_libs
    def DependsLibrariesString(self):
        return self._depends_libs_s

    def _MoveLibsFromDepends(self,libs):
        func_name='[_MoveLibsFromDepends]'
        for lib in libs:
            if(lib in self._depends_libs):
                self._depends_libs.remove(lib)
            else:
                msg='%s not found, please check it'%lib
                self._env.LogSystem().LogFatal('%s[err: %s]'%(func_name,msg))
        if(libs):
            self._depends_libs_s=self._line_delim.join(self._depends_libs)

    def _GetCompilerBinBySrc(self,srcs):
        for src in srcs:
            (_,ext)=os.path.splitext(src)
            if(ext!='.c'):
                return '$(CXX)'
        return '$(CC)'

    def Action(self):
        #Parse Arguments.并且设置Arguments.
        for arg in self._args:            
            if(isinstance(arg,SyntaxTag.TagPrefixes)):
                self._prefixes.extend(arg.V())
            elif(isinstance(arg,SyntaxTag.TagSources)):
                self._sources.extend(arg.V())            
        self._depends=self._env.Depends()
        
        #Action on Source Object.
        for source in self._sources:
            source.SetTarget(self)
            source.SetDepends(self._depends)
            source.PreAction()
        for source in self._sources:
            source.Action()

        self._sources_infiles=Function.Unique(
            map(lambda x:os.path.normpath(x.InFile()),
                self._sources))
        self._sources_outfiles=Function.Unique(
            map(lambda x:os.path.normpath(x.OutFile()),
                self._sources))
        
        #Analyze Depend.
        self._depends=filter(lambda x:x.Object()!=os.path.normpath(''),
                             self._depends)
        for depend in self._depends:
            self._depends_libs.append(os.path.join(depend.BasePath(self._env),
                                                   depend.Object()))
        self._depends_libs.sort(lambda x,y:cmp(x,y))
        self._depends_libs_s=self._line_delim.join(self._depends_libs)
        
class RUNCCP(Target):
    TYPE='ccp'
    
    def __init__(self,name,args,env):
        Target.__init__(self,name,args,env)
        self._target=self._name
    
    def Action(self):
        Target.Action(self)
        target=self._target
        self._phony_mode=True
        
        objs_s=self._line_delim.join(self._sources_outfiles)
        cpflags_s='-f' #copy选项.强制覆盖.        
        if(self._env.CopyUsingHardLink()):
            cpflags_s+=' --link'
            
        #Shell Commands.
        commands=[]
        targetfile='.%s.tag'%target 
        cmd='touch %(targetfile)s'%(locals())
        commands.append(cmd)
        commands.append('@echo "make %s done"'%target)
        r=(target,
           self._line_delim.join(self._prefixes+
                                 self._sources_outfiles),
           commands)
        self._make_lines.append(r)
        
        #Clean Commands.
        self._clean_files.append(targetfile)

class Application(Target):
    TYPE='app'
    
    def __init__(self,name,args,env):
        Target.__init__(self,name,args,env)
        self._target=self._name
    
    def Action(self):
        Target.Action(self)
        target=self._target
        output_path='./output/bin'
        
        #Parse Arguments.
        libs_flag=False
        ldflags_flag=False
        libs=[]
        ldflags=[]    
        link_libs=[]
        for arg in self._args:
            if(isinstance(arg,SyntaxTag.TagOutputPath)):
                output_path=arg.V()
            elif(isinstance(arg,SyntaxTag.TagLibraries)):
                libs_flag=True
                libs.extend(arg.V())
            elif(isinstance(arg,SyntaxTag.TagLinkFlags)):
                ldflags_flag=True
                ldflags.extend(arg.V())
            elif(isinstance(arg,SyntaxTag.TagLinkLibs)):
                link_libs.extend(arg.V())
            else:
                continue
        if(not libs_flag):
            libs=self._env.Libraries().V()
        if(not ldflags_flag):
            ldflags=self._env.LinkFlags().V()
        libs_s=self._line_delim.join(libs)
        ldflags_s=self._line_delim.join(ldflags)
        objs_s=self._line_delim.join(self._sources_outfiles)
        depends_libs_s=self._depends_libs_s
        cpflags_s='-f' #copy选项.强制覆盖.        
        if(self._env.CopyUsingHardLink()):
            cpflags_s+=' --link'
            
        #Shell Commands.
        #cxx=self._env.Cxx()
        cxx="$(CXX)"
        if(self._env.TimeCompileLink()):
            cxx='/usr/bin/time -avp -o %s/COMAKE.link.time.log %s'%(self._env.WorkRoot(),
                                                                    cxx)
        commands=[]
        if(link_libs):
            link_libs_s=self._line_delim.join(link_libs)
            cmd='%(cxx)s %(objs_s)s -Xlinker "-(" %(link_libs_s)s %(ldflags_s)s -Xlinker "-)" -o %(target)s'%(locals())
        else:  
            cmd='%(cxx)s %(objs_s)s -Xlinker "-(" %(libs_s)s '%(locals())
            cmd+='%(depends_libs_s)s %(ldflags_s)s -Xlinker "-)" -o %(target)s'%(locals())
        commands.append(cmd)
        if(output_path):
            commands.append('mkdir -p %(output_path)s'%(locals()))
            commands.append('cp %(cpflags_s)s %(target)s %(output_path)s'%(locals()))
        r=(target,
           self._line_delim.join(self._prefixes+
                                 self._sources_outfiles+
                                 libs),
           commands)
        self._make_lines.append(r)
        
        #Clean Commands.
        self._clean_files.append(target)
        if(output_path):
            self._clean_files.append(
                os.path.join(output_path,
                             os.path.basename(target)))

class StaticLibrary(Target):
    TYPE='lib'
    
    def __init__(self,name,args,env):
        Target.__init__(self,name,args,env)
        self._target=Function.AddPrefixToBaseName(
            Function.AddFileExtName(self._name,'.a'),
            'lib')
    
    def Action(self):
        Target.Action(self)
        target=self._target
        output_path="./output/lib"
        header_output_path="./output/include"
        
        #Parse Arguments.
        for arg in self._args:
            if(isinstance(arg,SyntaxTag.TagOutputPath)):
                output_path=arg.V()
            elif(isinstance(arg,SyntaxTag.TagHeaderOutputPath)):
                header_output_path=arg.V()
            elif(isinstance(arg,SyntaxTag.TagHeaderFiles)):
                self._header_files.extend(arg.V())
            else:
                continue
        objs_s=self._line_delim.join(self._sources_outfiles)
        cpflags_s='-f' #copy选项.
        if(self._env.CopyUsingHardLink()):
            cpflags_s+=' --link'

        #Shell Commands.
        commands=[]
        commands.append("ar crs %(target)s %(objs_s)s"%(locals()))
        if(output_path):
            commands.append("mkdir -p %(output_path)s"%(locals()))
            commands.append("cp %(cpflags_s)s %(target)s %(output_path)s"%(locals()))
        if(header_output_path and
           self._header_files):
            commands.append("mkdir -p %(header_output_path)s"%(locals()))
            commands.append("cp %s %s %s"%(cpflags_s,
                                           ' '.join(self._header_files),
                                           header_output_path))
        r=(target,
           self._line_delim.join(self._prefixes+
                                 self._sources_outfiles+
                                 self._header_files),
           commands)
        self._make_lines.append(r)

        #Clean Commands.
        self._clean_files.append(target)
        if(output_path):
            self._clean_files.append(
                os.path.join(output_path,
                             os.path.basename(target)))
        if(header_output_path):
            self._clean_files.extend(
                map(lambda x:os.path.join(header_output_path,
                                          os.path.basename(x)),
                    self._header_files))            

class SharedLibrary(Target):
    TYPE='so'
    
    def __init__(self,name,args,env):
        Target.__init__(self,name,args,env)
        self._target=Function.AddPrefixToBaseName(
            Function.AddFileExtName(self._name,'.so'),
            'lib')
        
    def Action(self):
        Target.Action(self)        
        target=self._target
        output_path="./output/so"
        header_output_path="./output/include"
        
        #Parse Arguments.
        libs_flag=False
        ldflags_flag=False
        #some users depend on previous default behaviour of sharedlibrary. 
        #warn them and then consider change default.
        #linkdeps_flags=True
        linkdeps_flags=False
        libs=[]
        ldflags=[]        
        whole_archive_libs=[]
        global warn_linkdeps_once
        for arg in self._args:
            if(isinstance(arg,SyntaxTag.TagOutputPath)):
                output_path=arg.V()
            elif(isinstance(arg,SyntaxTag.TagHeaderOutputPath)):
                header_output_path=arg.V()
            elif(isinstance(arg,SyntaxTag.TagHeaderFiles)):
                self._header_files.extend(arg.V())
            elif(isinstance(arg,SyntaxTag.TagLibraries)):
                libs_flag=True
                libs.extend(arg.V())
            elif(isinstance(arg,SyntaxTag.TagLinkFlags)):
                ldflags_flag=True
                ldflags.extend(arg.V())
            elif(isinstance(arg,SyntaxTag.TagLinkDepsFlags)):
                warn_linkdeps_once=True
                linkdeps_flags=arg.V()
            elif(isinstance(arg,SyntaxTag.TagWholeArchiveLibs)):
                whole_archive_libs.extend(arg.V())
            else:
                continue
        if(not warn_linkdeps_once):
            self._env.LogSystem().LogWarning('SharedLibrary links no dep libs: deprecated, specify SharedLibrary($lib,LinkDeps(False))')
            warn_linkdeps_once=True
        if(not libs_flag):
            libs=self._env.Libraries().V()
        if(not ldflags_flag):
            ldflags=self._env.LinkFlags().V()            

        libs_s=self._line_delim.join(libs)
        ldflags_s=self._line_delim.join(ldflags)
        objs_s=self._line_delim.join(self._sources_outfiles)
        depends_libs_s=self._depends_libs_s
        cpflags_s='-f' #copy选项.
        if(self._env.CopyUsingHardLink()):
            cpflags_s+=' --link'

        #Shell Commands.
        #生成命令和发布命令.
        #cc=self._env.Cc()
        cc=self._GetCompilerBinBySrc(self._sources_infiles)
        if(self._env.TimeCompileLink()):
            cc='/usr/bin/time -avp -o %s/COMAKE.link.time.log %s'%(self._env.WorkRoot(),
                                                                   cc)
        commands=[]
        if(linkdeps_flags==False):
            cmd='%(cc)s -shared %(objs_s)s -Xlinker "-(" %(libs_s)s %(ldflags_s)s -Xlinker "-)" -o %(target)s'%(locals())
        else:
            if(whole_archive_libs):
                whole_archive_libs_s=self._line_delim.join(whole_archive_libs)
                Target._MoveLibsFromDepends(self,whole_archive_libs)
                #self._depends_libs_s changed after _MoveLibsFromDepends
                depends_libs_s=self._depends_libs_s
                cmd='%(cc)s -shared %(objs_s)s -Xlinker "-(" --whole-archive %(whole_archive_libs_s)s --no-whole-archive %(libs_s)s %(depends_libs_s)s %(ldflags_s)s -Xlinker "-)" -o %(target)s'%(locals())
            else:
                cmd='%(cc)s -shared %(objs_s)s -Xlinker "-(" %(libs_s)s %(depends_libs_s)s %(ldflags_s)s -Xlinker "-)" -o %(target)s'%(locals())

        commands.append(cmd)
        if(output_path):
            commands.append("mkdir -p %(output_path)s"%(locals()))
            commands.append("cp %(cpflags_s)s %(target)s %(output_path)s"%(locals()))
        if(header_output_path and
           self._header_files):
            commands.append("mkdir -p %(header_output_path)s"%(locals()))
            commands.append("cp %s %s %s"%(cpflags_s,
                                           ' '.join(self._header_files),
                                           header_output_path))
        r=(target,
           self._line_delim.join(self._prefixes+
                                 self._sources_outfiles+
                                 self._header_files+
                                 libs),
           commands)
        self._make_lines.append(r)
                
        #Clean Commands.
        self._clean_files.append(target)
        if(output_path):
            self._clean_files.append(
                os.path.join(output_path,
                             os.path.basename(target)))
        if(header_output_path):
            self._clean_files.extend(
                map(lambda x:os.path.join(header_output_path,
                                          os.path.basename(x)),
                    self._header_files))
            
class SubDirectory(Target):
    TYPE='subdir'
    
    def __init__(self,name,args,env):
        Target.__init__(self,name,args,env)
        self._target=self._name
        
    def Action(self):
        Target.Action(self)
        target=self._target
        self._phony_mode=True
        
        #Analyze Depends.
        #目录之间会自动查找依赖...
        auto_prefixes=[]       
        if(os.path.exists(os.path.join(target,'COMAKE'))):
            cvspath=os.path.normpath(
                os.path.join(self._env.CVSPath(),
                             target))
            deps=self._env.SCMSystem().GetCompileDeps(cvspath,
                                                      '',#codetag
                                                      'COMAKE')
            for dep in deps:
                subdir=dep.CVSPath()[len(self._env.CVSPath())+1:]
                if(subdir in self._env.SubDirectories()):
                    auto_prefixes.append(subdir)

        #Shell Commands.
        commands=[]
        commands.append("@echo \"[%s][Entering directory:'%s']\""%(
                Function.GreenIt("COMAKE:BUILD"),
                Function.GreenIt(target)))
        commands.append("$(MAKE) -C %(target)s"%(locals()))
        commands.append("@echo \"[%s][Leaving directory:'%s']\""%(
                Function.GreenIt("COMAKE:BUILD"),
                Function.GreenIt(target)))
        r=(target,
           self._line_delim.join(self._prefixes+
                                 auto_prefixes),
           commands)
        self._make_lines.append(r)
        
        #Clean Commands.
        self._make_clean_lines.append("$(MAKE) -C %(target)s clean"%(locals()))

class FuzzTarget(Target):
    TYPE='fuzz'
    
    def __init__(self,name,args,env):
        Target.__init__(self,name,args,env)
        self._target=self._name

    def Action(self):
        Target.Action(self)    
        target=self._target
        
        #Parse Arguments.
        commands=[]
        commands_flag=False
        clean_commands=[]
        clean_files_flag=False
        for arg in self._args:
            if(isinstance(arg,SyntaxTag.TagPhonyMode)):
                self._phony_mode=arg.V()
            elif(isinstance(arg,SyntaxTag.TagCleanFiles)):
                clean_files_flag=True
                self._clean_files.extend(arg.V())
            elif(isinstance(arg,SyntaxTag.TagShellCommands)):
                commands_flag=True
                commands.extend(arg.V())
            elif(isinstance(arg,SyntaxTag.TagCleanCommands)):
                clean_commands.extend(arg.V())
                
        #如果没有指定命令的话,那么使用默认命令.
        if(not commands_flag):
            commands=['echo "build %(target)s over"'%(locals())]
            
        #Shell Commands.
        r=(target,
           self._line_delim.join(self._prefixes+
                                 self._sources_outfiles),
           commands)
        self._make_lines.append(r)

        #Clean Commands.
        if(not self._phony_mode and
           not clean_files_flag):
            self._clean_files.append(target)
        self._make_clean_lines.extend(clean_commands)


class NovaTestStub(Target):
    TYPE='nova-test-stub'
    
    def __init__(self,name,args,env):
        Target.__init__(self,name,args,env)
        self._target=self._name

    def Action(self):
        Target.Action(self)    
        target=self._target

        #Parse Arguments.
        libs_flag=False
        ldflags_flag=False
        libs=[]
        ldflags=[]    
        for arg in self._args:
            if(isinstance(arg,SyntaxTag.TagOutputPath)):
                output_path=arg.V()
            elif(isinstance(arg,SyntaxTag.TagLibraries)):
                libs_flag=True
                libs.extend(arg.V())
            elif(isinstance(arg,SyntaxTag.TagLinkFlags)):
                ldflags_flag=True
                ldflags.extend(arg.V())
            else:
                continue
        if(not libs_flag):
            libs=self._env.Libraries().V()
        if(not ldflags_flag):
            ldflags=self._env.LinkFlags().V()
        libs_s=self._line_delim.join(libs)
        ldflags_s=self._line_delim.join(ldflags)
        depends_libs_s=self._depends_libs_s
        objs_s=self._line_delim.join(self._sources_outfiles)
        #cxx=self._env.Cxx()
        cxx="$(CXX)"
        if(self._env.TimeCompileLink()):
            cxx='/usr/bin/time -avp -o %s/COMAKE.link.time.log %s'%(self._env.WorkRoot(),
                                                                    cxx)
        commands=[]
        cmd='%(cxx)s %(objs_s)s -rdynamic -Wl,--allow-multiple-definition '%(locals())
        cmd+='-Wl,--whole-archive -Xlinker "-(" %(libs_s)s %(depends_libs_s)s %(ldflags_s)s -Xlinker "-)" '%(locals())
        cmd+='-o %(target)s'%(locals())
        commands.append(cmd)
        r=(target,self._line_delim.join(self._sources_outfiles+libs),commands)
        self._make_lines.append(r)

        self._clean_files.append(target)
    
        
