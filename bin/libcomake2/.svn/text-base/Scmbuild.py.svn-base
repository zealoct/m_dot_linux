#!/usr/bin/env python

import os
import Function

class Scmbuild(object):
    def __init__(self,env,fname):
        self._env=env
        self._log=env.LogSystem()
        self._scm=env.SCMSystem()
        self._scm_file_name=fname

    def _ParseLines(self):
        if(not os.path.exists(self._scm_file_name)):
            msg='%s not exists, exit'%self._scm_file_name
            self._log.LogFatal(msg)
        self._scm_file=file(self._scm_file_name,'r')
        lines=self._scm_file.readlines()
        self._scm_file.close()
        self._lines=[]
        for i in range(len(lines)):
            if(lines[i][0]=='#'):
                continue
            if(lines[i].startswith(' '*4)):
                lines[i]=lines[i][4:]
                if(lines[i].startswith(' '*4)):
                    continue
            lines[i]=lines[i].strip()
            if(not lines[i]):
                continue
            secs=lines[i].split(',')
            if(len(secs)<6):
                msg="Line %d: \"%s\" is invalid!"%(i+1,lines[i])
                self._log.LogFatal(msg)
            self._lines.append(lines[i])
        cvspath=self._lines[0].split(',')[0]
        self._env.SetCVSPath(cvspath)

    def _Build(self,secs,run=True):
        func_name='[Action:Build]'
        cvspath=secs[0]
        if(run==False):
            if(not secs[4] and not secs[5]):
                return ''
            if(len(secs)>6 and secs[6]=='disbuild'):
                return ''
            if(not secs[4]):
                return 'cd %s;%s;cd -'%(cvspath,secs[5])
            return 'cd %s;%s;%s;cd -'%(cvspath,secs[4],secs[5])
        if(len(secs)>6 and secs[6]=='disbuild'):
            return
        if(secs[4]):
            command='cd %s;%s'%(cvspath,secs[4])
            (status,output,err)=self._log.LogNoticeWithCC(
                    '%s[cmd:%s]'%(func_name,
                              Function.GreenIt(command)),
                    command)
            if(status):
                self._log.LogWarning(
                    '%s[cvspath:%s][cmd:%s][status:%d][err:%s]'%(
                        func_name,
                        cvspath,
                        command,
                        status,
                        err))
        if(secs[5]):
            command='cd %s;%s'%(cvspath,secs[5])
            (status,output,err)=self._log.LogNoticeWithCC(
                    '%s[cmd:%s]'%(func_name,
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
 
    def Build(self):
        self._ParseLines()
        for line in self._lines[1:]:
            secs=line.split(',')
            self._Build(secs)

    def _Update(self,secs,run=True):
        if(secs[1]):
            rev=secs[1]
        else: 
            rev=secs[3]
        command=self._env._cs_handler.ScmCheckoutCommand(secs[0],rev,secs[2])
        if(run==False):
            return command
        (status,_,_)=self._env._cs_handler.ConnectSvn(command,maxrepeat=3,no_verify=True)
        if(status):
            msg="Fail to checkout %s"%secs[0]
            self._log.LogFatal(msg)
        return ''

    def Update(self):
        self._ParseLines()
        for line in self._lines:
            secs=line.split(',')
            self._Update(secs)
            
    def Export(self,export_file):
        if(os.path.exists(export_file)):
            msg="%s already exists, exit"%export_file
            self._log.LogFatal(msg)
        self._ParseLines()
        content_script=['#!/bin/sh\n\n']
        err_check='if [ $? -ne 0 ];then\n\techo Fail when run \\\"%s\\\"\n\texit 1\nfi\n\n'
        cvspath=self._lines[0].split(',')[0]
        for line in self._lines:
            secs=line.split(',')
            content_script.append('echo "[comake2] downloading %s ..."\n'%secs[0])
            cmd=self._Update(secs,run=False)
            content_script.append('echo "%s"\n'%cmd)
            content_script.append('%s\n'%cmd)
            content_script.append(err_check%cmd)
        for line in self._lines[1:]:
            secs=line.split(',')
            content_script.append('echo "[comake2] building %s ..."\n'%secs[0])
            cmd=self._Build(secs,run=False)
            if(cmd):
                content_script.append('echo "%s"\n'%cmd)
                content_script.append('%s\n'%cmd)
                content_script.append(err_check%cmd)
            else:
                content_script.append('echo "ignore %s as it does not need build or disabled"\n\n'%secs[0])
        content_script.append('echo comake2 build env ok!\n')
        content_script.append('echo Next, cd %s and build it on your own.\n'%cvspath)
        fp=file(export_file,'w')
        fp.writelines(content_script)
        fp.close()
        self._log.LogNotice('Generated %s ok.'%export_file)
        self._log.LogNotice('Next, run "sh %s" on your own.'%export_file)

