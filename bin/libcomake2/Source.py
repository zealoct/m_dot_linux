#!/usr/bin/env python
#coding:gbk
#Copyright (c) Baidu.com, Inc. All Rights Reserved 
#author:zhangyan04(@baidu.com)

import os
import glob
import string

import SyntaxTag
import Function

class Source(object):
    TYPE='source'
    def __init__(self,infile,args,env):
        self._infile=os.path.normpath(infile)
        self._outfile=self._infile
        self._args=args
        self._env=env
        self._log=env.LogSystem()
        self._target=None #Source对象外层Target对象.
        self._depends=[] #所依赖模块.
        
        self._make_lines=[]
        self._clean_files=[]
        self._incpaths=[]
        self._cxxflags=[]
        self._cppflags=[]
        self._cflags=[]
        self._idlflags=[]
        self._ubrpcflags=[]
        self._protoflags=[]
        self._use_mcy=True
        self._use_ubrpcgen=True
        self._prefixes=[] #依赖文件.
        self._line_delim=' \\\n  '
        self._space_delim=' '

        self._incpaths_flag=False
        self._cxxflags_flag=False
        self._cppflags_flag=False
        self._cflags_flag=False

        ###
        self._incpaths_s=''
        self._cxxflags_s=''
        self._cppflags_s=''
        self._cflags_s=''
        self._idlflags_s=''
        self._ubrpcflags_s=''
        self._protoflags_s=''
        self._depends_incpaths=[]
        self._depends_incpaths_s=''
        
    def __eq__(self,v):
        return self._infile==v._infile
    def InFile(self):
        return self._infile
    def Name(self):
        return self._infile
    def Target(self):
        return self._target
    def SetTarget(self,target):
        self._target=target
    def Env(self):
        return self._env 
    def Args(self):
        return self._args
    def MakeLines(self):
        return self._make_lines
    def OutFile(self):
        return self._outfile
    def CleanFiles(self):
        return self._clean_files
    def Depends(self):
        return self._depends
    def SetDepends(self,v):
        self._depends=v
    def UseMcy(self):
        return self._use_mcy
    def UseUbrpcgen(self):
        return self._use_ubrpcgen
    def _GetCPPBySrc(self):
        (_,ext)=os.path.splitext(self._infile)
        if(ext=='.idl'):
            return '%s -xc++'%self._env.Cxx()
        if(ext!='.c'):
            return self._env.Cxx()
        return self._env.Cc()
    
    def PreAction(self):
        func_name="[Action:PreAction]"
        idlflags_flag=False
        ubrpcflags_flag=False
        protoflags_flag=False

        #处理各类参数.
        for arg in self._args:
            if(isinstance(arg,SyntaxTag.TagIncludePaths)):
                self._incpaths_flag=True
                self._incpaths.extend(arg.V())
            elif(isinstance(arg,SyntaxTag.TagCxxFlags)):
                self._cxxflags_flag=True
                self._cxxflags.extend(arg.V())
            elif(isinstance(arg,SyntaxTag.TagCppFlags)):
                self._cppflags_flag=True 
                self._cppflags.extend(arg.V())
            elif(isinstance(arg,SyntaxTag.TagCFlags)):
                self._cflags_flag=True 
                self._cflags.extend(arg.V())
            elif(isinstance(arg,SyntaxTag.TagIdlFlags)):
                idlflags_flag=True
                self._idlflags.extend(arg.V())
            elif(isinstance(arg,SyntaxTag.TagUbRpcFlags)):
                ubrpcflags_flag=True
                self._ubrpcflags.extend(arg.V())
            elif(isinstance(arg,SyntaxTag.TagProtoFlags)):
                protoflags_flag=True
                self._protoflags.extend(arg.V())
            elif(isinstance(arg,SyntaxTag.TagUseMcy)):
                self._use_mcy=arg.V()
            elif(isinstance(arg,SyntaxTag.TagUseUbrpcgen)):
                self._use_ubrpcgen=arg.V()
            elif(isinstance(arg,SyntaxTag.TagPrefixes)):
                self._prefixes.extend(arg.V())
            else:
                continue
        #如果么有设置,使用默认的选项.
        if(not self._incpaths_flag):
            self._incpaths=self._env.IncludePaths().V()
        if(not self._cxxflags_flag):
            self._cxxflags=self._env.CxxFlags().V()
        if(not self._cppflags_flag):
            self._cppflags=self._env.CppFlags().V()
        if(not self._cflags_flag):
            self._cflags=self._env.CFlags().V()
        if(not idlflags_flag):
            self._idlflags=self._env.IdlFlags().V()
        if(not ubrpcflags_flag):
            self._ubrpcflags=self._env.UbRpcFlags().V()
        if(not protoflags_flag):
            self._protoflags=self._env.ProtoFlags().V()
            
        #各个选项的字符串表示.        
        self._incpaths_s=self._line_delim.join(map(lambda x:"-I%s"%x,
                                                   self._incpaths))
        self._cxxflags_s=self._line_delim.join(self._cxxflags)
        self._cppflags_s=self._line_delim.join(self._cppflags)
        self._cflags_s=self._line_delim.join(self._cflags)
        self._idlflags_s=self._line_delim.join(self._idlflags)
        self._ubrpcflags_s=self._line_delim.join(self._ubrpcflags)
        self._protoflags_s=self._line_delim.join(self._protoflags)
        
        #得到所有依赖库的includepaths.
        #然后把所有依赖路径凭借成为字符串并且需要去重排序
        #最后构成-I参数.
        #All the "_depends" depend on env.
        self._depends_incpaths=self._env.DependIncludePaths()
#       self._depends_incpaths=[]
#       for depend in self._depends:
#           self._depends_incpaths.extend(
#               map(lambda x:os.path.normpath(os.path.join(depend.BasePath(),x)),
#                   depend.IncludePaths()))
#       self._depends_incpaths=Function.Unique(self._depends_incpaths)
#       self._depends_incpaths.sort(lambda x,y:cmp(x,y))
        self._depends_incpaths_s=self._line_delim.join(
            map(lambda x:"-I%s"%x,
                self._depends_incpaths))
        
    def Action(self):
        pass

class IDLSource(Source):
    EXTS=('.idl',)
    TYPE='idl'
    def __init__(self,infile,args,env):
        Source.__init__(self,infile,args,env)
        
    def PreAction(self):
        """对IDL文件进行预处理,生成.h.cpp等文件"""
        Source.PreAction(self)
        func_name='[Action:PreAction]'
        #NOTICE(zhangyan04):对于idl文件,很多用户都是直接使用产出的文件
        #所以没有必要也不可能加上前缀.因为大部分用户都是使用mcy直接生成的.h和.cpp文件
        #同时需要注意所有自定义参数放在最后面,这样能够起到覆盖作用.
        idlfile=self._infile
        dirpath=os.path.dirname(idlfile)
        (root,_)=os.path.splitext(os.path.basename(idlfile))
        ofile=os.path.join(dirpath,root)
        ns=root
        idlflags_s=self._idlflags_s
        mcycmd=''
        self._idl_gen_hfiles=list()
        self._idl_gen_cxxfiles=list()
        if(self._use_mcy):
            mcy=self._env.McyBinary()
            mcycmd='%(mcy)s -o %(ofile)s --ns=%(ns)s %(idlflags_s)s %(idlfile)s'%(locals())
            (status,_,err)=self._log.LogNoticeWithCC(
                '%s[cmd:%s]'%(func_name,
                              Function.ShortenWord(mcycmd)),
                mcycmd)
            if(status):
                self._log.LogFatal('%s[cmd:%s][status:%d][err:%s]'%(
                        func_name,mcycmd,status,err))
            self._idl_gen_hfiles=['%s.h'%ofile]
            self._idl_gen_cxxfiles=['%s.cpp'%ofile]
        ubrpccmd=''
        ubrpcflags_s=self._ubrpcflags_s
        if(self._use_ubrpcgen):
            ubrpcgen=self._env.UbrpcgenBinary()
            ubrpccmd='%(ubrpcgen)s -o %(ofile)s --ns=%(ns)s %(ubrpcflags_s)s %(idlfile)s'%(locals())
            (status,_,err)=self._log.LogNoticeWithCC(
                '%s[cmd:%s]'%(func_name,
                              Function.ShortenWord(ubrpccmd)),
                ubrpccmd)
            if(status):
                self._log.LogFatal('%s[cmd:%s][status:%d][err:%s]'%(
                        func_name,ubrpccmd,status,err))
            flist=glob.glob('%s.*.h'%ofile)
            flist.sort()
            self._idl_gen_hfiles.extend(flist)
            flist=glob.glob('%s.*.cpp'%ofile)
            flist.sort()
            self._idl_gen_cxxfiles.extend(flist)
        
        #分析出IDL的依赖文件.首先我们必须得到所依赖-I参数.
        tmp_incflags=[]
        tmp_flags=self._idlflags+self._ubrpcflags
        i=0
        while(i<len(tmp_flags)):
            if(tmp_flags[i]=='-I'):
                if(i==(len(tmp_flags)-1)):
                    tmp_incflags.append('-I.')
                    i+=1
                else:
                    tmp_incflags.append('-I%s'%(tmp_flags[i+1]))
                    i+=2
            else:
                i+=1
        tmp_incflags_s=self._line_delim.join(Function.Unique(tmp_incflags))
        real_cc=self._env.Cxx()
        command1='%(real_cc)s -xc++ -MM -MG %(tmp_incflags_s)s %(idlfile)s'%(locals())
        command2='cpp -E %(tmp_incflags_s)s %(idlfile)s'%(locals())
        depfiles=[]
        depfiles.append(idlfile)
        depfiles.extend(GetCPPDependFiles(command1,command2,self._env,self._infile))
        commands=[]
        if(self._use_mcy):
            commands.append(mcycmd)
        if(self._use_ubrpcgen):
            commands.append(ubrpccmd)
            
        #添加规则.
        rules=[]
        r=(self._line_delim.join(self._idl_gen_cxxfiles+self._idl_gen_hfiles),
           self._line_delim.join(depfiles),
           commands)
        rules.append(r)
        self._clean_files.extend(self._idl_gen_cxxfiles+self._idl_gen_hfiles)
        for depfile in depfiles:
            r=(depfile,'',['@echo "ALREADY BUILT"'])
            rules.append(r)
        self._make_lines.extend(rules)
        
    def Action(self):
        Source.Action(self)
        gccflags_s="%(_incpaths_s)s %(_depends_incpaths_s)s "%(self.__dict__)
        gccflags_s+="%(_cppflags_s)s %(_cxxflags_s)s "%(self.__dict__)

        if(not self._incpaths_flag):
            r_gccflags_s="$(INCPATH) "
        else:
            r_gccflags_s="%(_incpaths_s)s "%(self.__dict__)

        r_gccflags_s+="$(DEP_INCPATH) "

        if(not self._cppflags_flag):
            r_gccflags_s+="$(CPPFLAGS) "
        else:
            r_gccflags_s+="%(_cppflags_s)s "%(self.__dict__)

        if(not self._cxxflags_flag):
            r_gccflags_s+="$(CXXFLAGS) "
        else:
            r_gccflags_s+="%(_cxxflags_s)s "%(self.__dict__)

        objfiles=[]
        real_cc=self._env.Cxx()
        for cxxfile in self._idl_gen_cxxfiles:
            objfile=Function.ReplaceFileExtName(
                Function.AddPrefixToBaseName(
                    cxxfile,
                    self._target.BaseName()+'_'),
                '.o')
            objfiles.append(objfile)
            command1='%(real_cc)s -MG -MM %(gccflags_s)s %(cxxfile)s'%(locals())
            command2='cpp -E %(gccflags_s)s %(cxxfile)s'%(locals())
            depfiles=[]
            depfiles.append(cxxfile)
            depfiles.extend(self._prefixes)
            depfiles.extend(GetCPPDependFiles(command1,command2,self._env,cxxfile))
            cxx="$(CXX)"
            if(self._env.TimeCompileLink()):
                cxx='/usr/bin/time -avp -o %s/COMAKE.compile.time.log %s'%(self._env.WorkRoot(),
                                                                           cxx)
            cmd='%(cxx)s -c %(r_gccflags_s)s -o %(objfile)s %(cxxfile)s'%(locals())
            commands=[]
            commands.append(cmd)
            r=(objfile,
               self._line_delim.join(depfiles),
               commands)
            self._make_lines.append(r)
        self._clean_files.extend(objfiles)
        self._outfile=self._line_delim.join(objfiles)

class ProtoSource(Source):
    EXTS=('.proto',)
    TYPE='proto'
    def __init__(self,infile,args,env):
        Source.__init__(self,infile,args,env)
        
    def PreAction(self):
        """对proto文件进行预处理,生成.h.cc 等文件"""
        Source.PreAction(self)
        func_name='[Action:PreAction]'
        #NOTICE(zhangyan04):对于idl文件,很多用户都是直接使用产出的文件
        #所以没有必要也不可能加上前缀.因为大部分用户都是使用mcy直接生成的.h和.cpp文件
        #同时需要注意所有自定义参数放在最后面,这样能够起到覆盖作用.
        protofile=self._infile
        protoflags_s=self._protoflags_s
        protobin=self._env.ProtoBinary()
        dirpath=os.path.dirname(protofile)
        if(dirpath==''):
            dirpath='./'
        protocmd='%(protobin)s --cpp_out=%(dirpath)s --proto_path=%(dirpath)s %(protoflags_s)s %(protofile)s'%(locals())
        (status,_,err)=self._log.LogNoticeWithCC(
                '%s[cmd:%s]'%(func_name,
                              Function.ShortenWord(protocmd)),
                protocmd)
        if(status):
            self._log.LogFatal('%s[cmd:%s][status:%d][err:%s]'%(
                        func_name,protocmd,status,err))
        (root,_)=os.path.splitext(os.path.basename(protofile))
        ofile=os.path.join(dirpath,root)
        self._proto_gen_hfiles=['%s.pb.h'%ofile]
        self._proto_gen_cxxfiles=['%s.pb.cc'%ofile]
        
        #添加规则.
        rules=[]
        r=(self._line_delim.join(self._proto_gen_cxxfiles+self._proto_gen_hfiles),
           protofile,
           [protocmd])
        rules.append(r)
        self._clean_files.extend(self._proto_gen_cxxfiles+self._proto_gen_hfiles)
        r=(protofile,'',['@echo "ALREADY BUILT"'])
        rules.append(r)
        self._make_lines.extend(rules)
        
    def Action(self):
        Source.Action(self)
        gccflags_s="%(_incpaths_s)s %(_depends_incpaths_s)s "%(self.__dict__)
        gccflags_s+="%(_cppflags_s)s %(_cxxflags_s)s "%(self.__dict__)

        if(not self._incpaths_flag):
            r_gccflags_s="$(INCPATH) "
        else:
            r_gccflags_s="%(_incpaths_s)s "%(self.__dict__)

        r_gccflags_s+="$(DEP_INCPATH) "

        if(not self._cppflags_flag):
            r_gccflags_s+="$(CPPFLAGS) "
        else:
            r_gccflags_s+="%(_cppflags_s)s "%(self.__dict__)

        if(not self._cxxflags_flag):
            r_gccflags_s+="$(CXXFLAGS) "
        else:
            r_gccflags_s+="%(_cxxflags_s)s "%(self.__dict__)

        objfiles=[]
        real_cc=self._env.Cxx()
        for cxxfile in self._proto_gen_cxxfiles:
            objfile=Function.ReplaceFileExtName(
                Function.AddPrefixToBaseName(
                    cxxfile,
                    self._target.BaseName()+'_'),
                '.o')
            objfiles.append(objfile)
            command1='%(real_cc)s -MG -MM %(gccflags_s)s %(cxxfile)s'%(locals())
            command2='cpp -E %(gccflags_s)s %(cxxfile)s'%(locals())
            depfiles=[]
            depfiles.append(cxxfile)
            depfiles.extend(self._prefixes)
            depfiles.extend(GetCPPDependFiles(command1,command2,self._env,cxxfile))
            cxx="$(CXX)"
            if(self._env.TimeCompileLink()):
                cxx='/usr/bin/time -avp -o %s/COMAKE.compile.time.log %s'%(self._env.WorkRoot(),
                                                                           cxx)
            cmd='%(cxx)s -c %(r_gccflags_s)s -o %(objfile)s %(cxxfile)s'%(locals())
            commands=[]
            commands.append(cmd)
            r=(objfile,
               self._line_delim.join(depfiles),
               commands)
            self._make_lines.append(r)
        self._clean_files.extend(objfiles)
        self._outfile=self._line_delim.join(objfiles)

class CSource(Source):
    """C Source Code"""
    EXTS=('.c',)
    TYPE='c'
    def __init__(self,infile,args,env):
        Source.__init__(self,infile,args,env)
    def PreAction(self):
        Source.PreAction(self)
    def Action(self):
        Source.Action(self)
        cfile=self._infile
        objfile=Function.ReplaceFileExtName(
            Function.AddPrefixToBaseName(
                cfile,
                self._target.BaseName()+'_'),
            '.o')
        gccflags_s="%(_incpaths_s)s %(_depends_incpaths_s)s "%(self.__dict__)
        gccflags_s+="%(_cppflags_s)s %(_cflags_s)s "%(self.__dict__)
        real_cc=self._env.Cc()
        command1='%(real_cc)s -MG -MM %(gccflags_s)s %(cfile)s'%(locals())
        command2='cpp -E %(gccflags_s)s %(cfile)s'%(locals())
        depfiles=[]
        depfiles.append(cfile)
        depfiles.extend(self._prefixes)
        depfiles.extend(GetCPPDependFiles(command1,command2,self._env,self._infile))
        cc="$(CC)"
        if(self._env.TimeCompileLink()):
            cc='/usr/bin/time -avp -o %s/COMAKE.compile.time.log %s'%(self._env.WorkRoot(),
                                                                     cc)

        if(not self._incpaths_flag):
            r_gccflags_s="$(INCPATH) "
        else:
            r_gccflags_s="%(_incpaths_s)s "%(self.__dict__)

        r_gccflags_s+="$(DEP_INCPATH) "

        if(not self._cppflags_flag):
            r_gccflags_s+="$(CPPFLAGS) "
        else:
            r_gccflags_s+="%(_cppflags_s)s "%(self.__dict__)

        if(not self._cflags_flag):
            r_gccflags_s+="$(CFLAGS) "
        else:
            r_gccflags_s+="%(_cflags_s)s "%(self.__dict__)

        cmd='%(cc)s -c %(r_gccflags_s)s -o %(objfile)s %(cfile)s'%(locals())
        commands=[]
        commands.append(cmd)
        r=(objfile,self._line_delim.join(depfiles),commands)
        self._make_lines.append(r)
        self._clean_files.append(objfile)
        self._outfile=objfile
        
class CXXSource(Source):
    """C++ Source Code"""
    EXTS=('.cpp','.cc','.cxx')
    TYPE='cxx'
    def __init__(self,infile,args,env):
        Source.__init__(self,infile,args,env)

    def PreAction(self):
        Source.PreAction(self)

    def Action(self):
        Source.Action(self)
        cxxfile=self._infile
        objfile=Function.ReplaceFileExtName(
            Function.AddPrefixToBaseName(
                cxxfile,
                self._target.BaseName()+'_'),
            '.o')
        gccflags_s="%(_incpaths_s)s %(_depends_incpaths_s)s "%(self.__dict__)
        gccflags_s+="%(_cppflags_s)s %(_cxxflags_s)s "%(self.__dict__)
        real_cc=self._env.Cxx()
        command1='%(real_cc)s -MG -MM %(gccflags_s)s %(cxxfile)s'%(locals())
        command2='cpp -E %(gccflags_s)s %(cxxfile)s'%(locals())
        depfiles=[]
        depfiles.append(cxxfile)
        depfiles.extend(self._prefixes)
        depfiles.extend(GetCPPDependFiles(command1,command2,self._env,self._infile))
        cxx="$(CXX)"
        if(self._env.TimeCompileLink()):
            cxx='/usr/bin/time -avp -o %s/COMAKE.compile.time.log %s'%(self._env.WorkRoot(),
                                                                       cxx)

        if(not self._incpaths_flag):
            r_gccflags_s="$(INCPATH) "
        else:
            r_gccflags_s="%(_incpaths_s)s "%(self.__dict__)

        r_gccflags_s+="$(DEP_INCPATH) "

        if(not self._cppflags_flag):
            r_gccflags_s+="$(CPPFLAGS) "
        else:
            r_gccflags_s+="%(_cppflags_s)s "%(self.__dict__)

        if(not self._cxxflags_flag):
            r_gccflags_s+="$(CXXFLAGS) "
        else:
            r_gccflags_s+="%(_cxxflags_s)s "%(self.__dict__)

        cmd='%(cxx)s -c %(r_gccflags_s)s -o %(objfile)s %(cxxfile)s'%(locals())
        commands=[]
        commands.append(cmd)
        r=(objfile,self._line_delim.join(depfiles),commands)
        self._make_lines.append(r)
        self._clean_files.append(objfile)
        self._outfile=objfile

class FileSource(Source):
    def __init__(self,infile,args,env):
        Source.__init__(self,infile,args,env)

    def PreAction(self):
        Source.PreAction(self)

    def Action(self):
        Source.Action(self)

class CCPSource(Source):
    """CCP Source Code"""
    #EXTS=('.cpp','.cc','.cxx')
    TYPE='ccp'
    def __init__(self,infile,args,env):
        Source.__init__(self,infile,args,env)
        self._ccpdriver=''
        # _ccp_flags vs. _cppflags. Easy confusing...
        self._ccp_flags=[]
        self._ccp_flags_s=''
        self._use_incpaths=False

    def PreAction(self):
        func_name="[Action:PreAction]"
        Source.PreAction(self)
        ccp_driver_flag=False
        ccp_flags_flag=False

        #处理各类参数.
        for arg in self._args:
            if(isinstance(arg,SyntaxTag.TagCCPDriver)):
                ccp_driver_flag=True
                self._ccp_driver=arg.V()
            elif(isinstance(arg,SyntaxTag.TagCCPFlags)):
                ccp_flags_flag=True
                self._ccp_flags.extend(arg.V())
            elif(isinstance(arg,SyntaxTag.TagCCPUseIncPaths)):
                self._use_incpaths=True

        #如果么有设置,使用默认的选项.
        targetname=self._target.BaseName()
        if targetname.startswith('pclint'):
            self._use_incpaths=True
            if(not ccp_driver_flag):
                self._ccp_driver='$(PCLINT)'
            if(not ccp_flags_flag):
                self._ccp_flags_s='$(PCLINT_FLAGS)'
        elif targetname.startswith('ccheck'):
            self._use_incpaths=True
            if(not ccp_driver_flag):
                self._ccp_driver='$(CCHECK)'
            if(not ccp_flags_flag):
                self._ccp_flags_s='$(CCHECK_FLAGS)'

        if(ccp_flags_flag):
            self._ccp_flags_s=' '.join(self._ccp_flags)

    def Action(self):
        Source.Action(self)
        ccpfile=self._infile
        tagfile=Function.AddFileExtName(
            Function.AddPrefixToBaseName(
                ccpfile,
                '.'+self._target.BaseName()+'_'),
            '.tag')
        gccflags_s="%(_incpaths_s)s %(_depends_incpaths_s)s "%(self.__dict__)
        gccflags_s+="%(_cppflags_s)s "%(self.__dict__)
        real_cc=self._GetCPPBySrc() 
        command1='%(real_cc)s -MG -MM %(gccflags_s)s %(ccpfile)s'%(locals())
        command2='cpp -E %(gccflags_s)s %(ccpfile)s'%(locals())
        depfiles=[]
        depfiles.append(ccpfile)
        depfiles.extend(self._prefixes)
        (_,ext)=os.path.splitext(ccpfile)
        if(ext!='.h' and ext!='.hpp'):
            depfiles.extend(GetCPPDependFiles(command1,command2,self._env,self._infile))
        
        r_gccflags_s=''
        if self._use_incpaths:
            if(not self._incpaths_flag):
                r_gccflags_s="$(INCPATH) "
            else:
                r_gccflags_s="%(_incpaths_s)s "%(self.__dict__)

            r_gccflags_s+="$(DEP_INCPATH) "

            if(not self._cppflags_flag):
                r_gccflags_s+="$(CPPFLAGS) "
            else:
                r_gccflags_s+="%(_cppflags_s)s "%(self.__dict__)

        ccp_driver=self._ccp_driver
        ccp_flags_s=self._ccp_flags_s
        cmd='%(ccp_driver)s %(ccp_flags_s)s %(r_gccflags_s)s %(ccpfile)s'%(locals())
        commands=[]
        commands.append(cmd)
        cmd='touch %(tagfile)s'%(locals())
        commands.append(cmd)
        r=(tagfile,self._line_delim.join(depfiles),commands)
        self._make_lines.append(r)
        self._clean_files.append(tagfile)
        self._outfile=tagfile

def GetCPPDependFiles(command1,command2,env,infile):
    """分析command1产生输出,如果没有成功.
    执行command2.command1执行失败,command2必然执行失败.
    针对cpp预处理分析处理的"""
    func_name='[Action:GetCPPDependFiles]'
    log=env.LogSystem()
    a=os.getenv('PRE')                                
    if a=='True':                                     
        (status,output,err)=(0,":","")                
    else:
        (status,output,err)=log.LogNoticeWithCC('%s[cmd:%s]'%(func_name,Function.ShortenWord(command1)),command1)
    if(status):                                       
        log.LogFatal('%s[cmd:%s][status:%d][err:%s]'%(func_name,
                                                      command1,
                                                      status,
                                                      err))
    line=' '.join(string.split(output,'\\\n'))
    depfiles=string.split(string.split(line,':')[1])
    cwd='%s/'%(os.path.abspath(os.getcwd()))    
    a=os.getenv('QUOT_ALL_DEPS')                                
    if a!='True':                                     
        depfiles=map(lambda x:os.path.normpath(x),
                 filter(lambda x:os.path.abspath(x).startswith(cwd),
                        depfiles))
    for depfile in depfiles:        
        if(not os.path.exists(depfile)):
            (status,_,err)=log.LogDebugWithCC(
                '%s[cmd:%s]'%(func_name,
                              Function.ShortenWord(command2)),
                command2)
            assert(status)
            log.LogFatal('%s[cmd:%s][status:%d][err:%s]'%(func_name,
                                                          command2,
                                                          status,
                                                          err))

    if(depfiles and infile==depfiles[0]):
        depfiles=depfiles[1:]

    return depfiles
