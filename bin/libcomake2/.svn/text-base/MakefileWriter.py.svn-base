#!/usr/bin/env python
#coding:gbk
#Copyright (c) Baidu.com, Inc. All Rights Reserved 
#author:zhangyan04(@baidu.com)

import os
import Function
import Target
import Source

"""
每一个Makefile对应的Line,包括三个部分(target,deps,commands)
其中target,deps都是字符串形式,commands是一个字符串列表
"""

class MakefileWriter(object):
    def __init__(self):
        self._lines=[]
        self.mfname=''

    def All(self):
        r0=('.PHONY','all',[])
        r1_dep='comake2_makefile_check '
        for exp in self._env.Exports():
            r1_dep+='%s '%(exp)
        r1=('all',r1_dep,['@echo "make all done"'])
        #检查COMAKE文件是否比Makefile文件要更新.
        r2=('.PHONY','comake2_makefile_check',[])
        md5_file='comake2.md5'
        commands=[]
        commands.append("#in case of error, update 'Makefile' by 'comake2'")
        commands.append('@echo "$(COMAKE_MD5)">%s'%md5_file)
        commands.append('@md5sum -c --status %s'%md5_file)
        commands.append("@rm -f %s"%md5_file)
        r3=('comake2_makefile_check','',commands)
        return (r0,r1,r2,r3)
    
    def Clean(self):
        r0=('.PHONY','clean',[])
        commands=[]
        for target in self._env.Targets():
	    if(target.TYPE==Target.RUNCCP.TYPE):
                continue
            for x in target.CleanFiles():                
                commands.append('rm -rf %s'%(x))
            commands.extend(target.MakeCleanLines())
        sources=Function.Unique(self._env.Sources(),
                                lambda x:x.OutFile())
        for source in sources:
	    if(source.TYPE==Source.CCPSource.TYPE):
                continue
            for x in source.CleanFiles():
                commands.append('rm -rf %s'%(x))
        r1=('clean','ccpclean',commands)
        return (r0,r1)
    
    def CcpClean(self):
        r0=('.PHONY','ccpclean',[])
        commands=[]
        for target in self._env.Targets():
	    if(target.TYPE==Target.RUNCCP.TYPE):
                for x in target.CleanFiles():                
                    commands.append('rm -rf %s'%(x))
                commands.extend(target.MakeCleanLines())
                sources=Function.Unique(target.SourcesOutFiles())
                for source in sources:
                    commands.append('rm -rf %s'%(source))
        commands.append('@echo "make ccpclean done"')
        r1=('ccpclean','',commands)
        return (r0,r1)

    def Love(self):
        r0=('.PHONY','love',[])
        r1=('love','',['@echo "make love done"'])
        return (r0,r1)

    def Dist(self):
        r0=('.PHONY','dist',[])
        commands=[]
        directory='output'
        commands.append('tar czvf %(directory)s.tar.gz %(directory)s'%(locals()))
        commands.append('@echo "make dist done"')
        r1=('dist','',commands)
        return (r0,r1)
    
    def DistClean(self):
        r0=('.PHONY','distclean',[])
        commands=[]
        directory='output'
        commands.append('rm -f %(directory)s.tar.gz'%(locals()))
        commands.append('@echo "make distclean done"')
        r1=('distclean','clean',commands)
        return (r0,r1)
    
    def Collect(self,env):
        self._env=env

        if (not self._env.Multilibs()):
            self.mfname='Makefile'
        elif os.popen('uname -m').read() == 'x86_64\n':
            self.mfname='Makefile.64'
            self.GentleMakefile()
        else:
            self.mfname='Makefile.32'
            self.GentleMakefile()

        make_lines=[]
        make_lines.extend(self.All())
        make_lines.extend(self.CcpClean())
        make_lines.extend(self.Clean())
        make_lines.extend(self.Dist())
        make_lines.extend(self.DistClean())
        make_lines.extend(self.Love())
        ccptargets=[]
        for target in self._env.Targets():
            if(target.PhonyMode()):
                r=('.PHONY',target.Target(),[])
                make_lines.append(r)
            make_lines.extend(target.MakeLines())
            if(target.TYPE==Target.RUNCCP.TYPE):
                ccptargets.append(target.Target())
        if ccptargets!=[]:
            ccp=self._env.CcpTarget()
            r=('.PHONY',ccp,[])
            make_lines.append(r)
            r=(ccp,' '.join(ccptargets),['@echo "make %s done"'%ccp])
            make_lines.append(r)
        for source in self._env.Sources():
            make_lines.extend(source.MakeLines())
            
        #make lines也可能会存在重复的内容..:).
        make_lines=Function.Unique(make_lines,
                                   lambda x:(x[0],x[1]))
        
        #将make_lines格式转换成为Makefile格式.
        lines=[]
        #Print env variables at the header of Makefile.
        self._env.Print(lines)
        for x in make_lines:
            (t,dep,cmds)=x
            lines.append('%s:%s'%(t,dep))
            if(not cmds):
                continue
            lines.append("\t@echo \"[%s][Target:'%s']\""%(
                    Function.GreenIt("COMAKE:BUILD"),
                    Function.GreenIt(t)))
            for cmd in cmds:
                lines.append("\t%s"%(cmd))
            #seperate lines.
            lines.append('')

        #针对32/64平台操作.
        self._lines.append(
            '####################%dBit Mode####################\n'%(
                env.Bit()))
        self._lines.append('ifeq ($(shell uname -m),%s)\n'%(self._env.CPU()))
        self._lines.extend(map(lambda x:'%s\n'%x,lines))
        self._lines.append('endif #ifeq ($(shell uname -m),%s)\n\n\n'%(self._env.CPU()))
            
    def Write(self):
        #需要添加头,这样以便后续可以扩展.
        header_lines=['#COMAKE2 edit-mode: -*- Makefile -*-\n']
        fp=open('%s'%self.mfname,'w')
        fp.writelines(header_lines+self._lines)
        fp.close()

    def GentleMakefile(self):
        fp=open('Makefile','w')
        header_lines='#COMAKE2 edit-mode: -*- Makefile -*-\n'
        context='''HARDWARE_PLATFORM := $(shell uname -m)
ifeq ($(HARDWARE_PLATFORM),x86_64)
    release=Makefile.64
else
    release=Makefile.32
endif
all:
\tmake -f $(release)
clean:
\tmake clean -f $(release)
dist:
\tmake dist -f $(release)
'''
        contexts=[header_lines,context]
        for target in self._env.Targets():
            tar=target.Target()
            contexts.append('%s:\n\tmake %s -f $(release)\n'%(tar,tar))
        fp.write(''.join(contexts))
        fp.close()
 
