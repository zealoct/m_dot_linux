#!/usr/bin/env python
#coding:gbk
#Copyright (c) Baidu.com, Inc. All Rights Reserved 
#author:zhangyan04(@baidu.com)

import os
import sys
import string
import urllib2
import Function
import time
import socket
from xml.dom.minidom import parseString

SVN_SERVER='https://svn.baidu.com'

IS_EXISTS=0
NO_EXISTS=1
NO_PERMISSION=2

svn_servlet_cache=dict()

class BaiduSVNCodeSystem(object):
    UNKNOWN='???'
    def __init__(self,env):
        self._env=env
        self._log=env.LogSystem()
        self._scm=env.SCMSystem()
        self._svn_urls_cache={}
        self._keep_going=False
        self._no_revert=False
        self._UPDATED_TAG='.COMAKE.UPDATED.TAG'
        self._UPDATED_REVISION='.COMAKE.UPDATED.REVISION'
        self._update_tabs=list()
        self._network_line_diskcache_dir=os.path.join(
            os.environ['HOME'],'.COMAKE.CACHE/svn_dir_trees')

    def SetKeepGoing(self,k):
        self._keep_going=k

    def SetNoRevert(self,k):
        self._no_revert=k

    def SetParallelUpdates(self,k):
        for i in range(k):
            self._update_tabs.append((None, None))

    def ResetUpdates(self):
        for i in range(len(self._update_tabs)):
            self._update_tabs[i] = (None, None)
      
    def EnableParallelUpdates(self):
        return len(self._update_tabs)>=2
     
    def _FileForRecordRevision(self, basepath): 
        return  "/tmp/%s%s"%(os.path.abspath(basepath).replace("/", "."), self._UPDATED_REVISION)
  
    def _GetRevisionFromFile(self, cfg):
        basepath = cfg.BasePath(self._env)
        recordfile = self._FileForRecordRevision(basepath)
        f = open(recordfile, "r")
        cfg._revision = f.read()
        f.close()
        os.remove(recordfile)

    def _GetIdleThread(self):
        for i in range(len(self._update_tabs)):
            pid, cfg = self._update_tabs[i]
            if pid==None:
                return i
            wpid, status = os.waitpid(pid, os.WNOHANG)
            if wpid > 0:
                self._update_tabs[i] = (None, None)
                if status!=0:
                    self.WaitOtherUpdatesFinish()
                    sys.exit(1)
                elif cfg:
                    self._GetRevisionFromFile(cfg)
                return i
        return -1

    def WaitOtherUpdatesFinish(self):
        result=0
        for i in range(len(self._update_tabs)):
            pid, cfg = self._update_tabs[i]
            if pid==None:
                continue
            wpid, status = os.waitpid(pid, 0)
            if status!=0:
                result=1
            elif cfg:
                self._GetRevisionFromFile(cfg)
            self._update_tabs[i] = (None, None)
        return result

    def _SplitCVSPath(self,cvspath):
        """拆分cvspath,分别得到:
        1.trunk
        2.branches
        3.tags
        """
        func_name='[Action:_SplitCVSPath]'
        if(cvspath in svn_servlet_cache):
           return svn_servlet_cache[cvspath]
        cache_file=os.path.join(self._network_line_diskcache_dir,
                                cvspath.replace('/','.'))
        if(self._env.ReCache()==False and os.path.exists(cache_file)):
            line=open(cache_file).read()
            svn_servlet_cache[cvspath]=eval(line)
            return svn_servlet_cache[cvspath]
        SERVICE_URL='http://svn.baidu.com:8000/svnlogistics/SVNGlueServlet.action?path='
        req_url='%s%s'%(SERVICE_URL,cvspath)
        self._log.LogDebug('%s[req_url:%s]'%(func_name,req_url),2)
        URL_TIMEOUT=60
        socket.setdefaulttimeout(URL_TIMEOUT)
        i=0
        while(True):
            try:
                data=urllib2.urlopen(req_url).read()
            except urllib2.URLError,e:
                if(i>=5):
                    self._log.LogFatal('%s:[req_url:%s][urllib2.URLError:%s]'%(
                                       func_name,req_url,e))
                i=i+1
                continue
            break
        #结构是这样的(public/trunk/ub,public/branches/ub,public/tags/ub)
        #可以直接使用eval().
        if not data:
            self._log.LogFatal('非法cvspath: %s'%cvspath)
        try:
            if(not os.path.exists(self._network_line_diskcache_dir)):
                os.makedirs(self._network_line_diskcache_dir)
            open(cache_file,'w').write(data)
        except Exception,e:
            self._log.LogDebug("%s:[cache_file:%s][Exception:%s]"%(
                    func_name,cache_file,e))
        """before eval:
        data='("ibase/trunk/gm","ibase/branches/gm","ibase/tags/gm")'
           after eval:
        data=("ibase/trunk/gm","ibase/branches/gm","ibase/tags/gm")"""
        data=eval(data)
        svn_servlet_cache[cvspath]=data
        return data
    
    def _GetSVNURLs(self,cvspath):
        if(cvspath in self._svn_urls_cache):
            return self._svn_urls_cache[cvspath]
        urls=map(lambda x:'%s/%s/'%(SVN_SERVER,x),
                 self._SplitCVSPath(cvspath))
        self._svn_urls_cache[cvspath]=urls
        return urls
        
    def SwitchCommand(self,cfg,force=False):
        (trunk,branches,tags)=self._GetSVNURLs(cfg.CVSPath())
        workroot=self._env.WorkRoot()
        (basepath,cvspath,codetag,revision)=(cfg.BasePath(self._env),
                                    cfg.CVSPath(),
                                    cfg.CodeTag(),
                                    cfg.Revision())
        #!force.
        if(not force):
            if(self._no_revert==False):
                if(self._scm.IsTagTrunk(codetag)):
                    command='cd %(basepath)s&&svn -R revert .&&svn switch %(trunk)s -r %(revision)s'%(locals())
                elif(self._scm.IsTagBranch(codetag)):
                    command='cd %(basepath)s&&svn -R revert .&&svn switch %(branches)s%(codetag)s -r %(revision)s'%(locals())
                else:
                    command='cd %(basepath)s&&svn -R revert .&&svn switch %(tags)s%(codetag)s'%(locals())
            else:
                if(self._scm.IsTagTrunk(codetag)):
                    command='cd %(basepath)s&&svn switch %(trunk)s -r %(revision)s'%(locals())
                elif(self._scm.IsTagBranch(codetag)):
                    command='cd %(basepath)s&&svn switch %(branches)s%(codetag)s -r %(revision)s'%(locals())
                else:
                    command='cd %(basepath)s&&svn switch %(tags)s%(codetag)s'%(locals()) 
        #force.
        else:
            #如果是强制切换的话,那么必须首先删除原来内容,然后重新下载.
            if(self._scm.IsTagTrunk(codetag)):
                command='cd %(workroot)s;rm -rf %(cvspath)s;svn co %(trunk)s %(cvspath)s -r %(revision)s'%(locals())
            elif(self._scm.IsTagBranch(codetag)):
                command='cd %(workroot)s;rm -rf %(cvspath)s;svn co %(branches)s%(codetag)s %(cvspath)s -r %(revision)s'%(locals())
            else:
                command='cd %(workroot)s;rm -rf %(cvspath)s;svn co %(tags)s%(codetag)s %(cvspath)s'%(locals())
        return command

    def IsTagExists(self,cvspath,codetag):
        func_name='[Action:IsTagExists]'
        (trunk,branches,tags)=self._GetSVNURLs(cvspath)
        if(self._scm.IsTagTrunk(codetag)):
            command='svn ls %(trunk)s'%(locals())
        elif(self._scm.IsTagBranch(codetag)):
            command='svn ls %(branches)s%(codetag)s'%(locals())
        else:
            command='svn ls %(tags)s%(codetag)s'%(locals())
        (status,output,err)=self._log.LogDebugWithCC(
            '%s[cmd:%s]'%(func_name,command),
            command,
            2)
        if(status):
            if(err.__contains__('403 Forbidden')):
                return NO_PERMISSION
            return NO_EXISTS
        return IS_EXISTS

    def _BackupModif(self,cfg):
        func_name='[Action:_BackupModif]'
        bkdir='%s/.COMAKE.TMP'%os.getenv('HOME')
        if(not os.path.exists(bkdir)):
            os.mkdir(bkdir)
        cvspath=cfg.CVSPath()
        subdir=cvspath.replace('/','.')
        ctime=time.strftime("%Y%m%d.%H%M%S", time.localtime())
        subdir='%s/%s.%s'%(bkdir,subdir,ctime)

        basepath=cfg.BasePath(self._env)
        command='cp -r %(basepath)s %(subdir)s'%(locals())
        (status,output,err)=self._log.LogNoticeWithCC(
            '%s[cmd:%s]'%(func_name,command),
            command,
            2)
        if(status):
            self._log.LogFatal('%s[cmd:%s][status:%d][err:%s]'%(func_name,
                                                                command,
                                                                status,
                                                                err))

    def CheckoutCommand(self,cfg):
        (trunk,branches,tags)=self._GetSVNURLs(cfg.CVSPath())
        workroot=self._env.WorkRoot()
        (cvspath,codetag,revision)=(cfg.CVSPath(),
                                    cfg.CodeTag(),
                                    cfg.Revision())
        if(self._scm.IsTagTrunk(codetag)):
            command='cd %(workroot)s;svn co %(trunk)s %(cvspath)s -r %(revision)s'%(locals())
        elif(self._scm.IsTagBranch(codetag)):
            command='cd %(workroot)s;svn co %(branches)s%(codetag)s %(cvspath)s -r %(revision)s'%(locals())
        else:
            command='cd %(workroot)s;svn co %(tags)s%(codetag)s %(cvspath)s'%(locals())
        return command
    
    def ExportCOMAKECommand(self, cvspath, codetag, revision, comakefile):
        (trunk,branches,tags)=self._GetSVNURLs(cvspath)
        workroot=self._env.WorkRoot()
        if(self._scm.IsTagTrunk(codetag)):
            if(revision==''):
                command='cd %(workroot)s;svn export %(trunk)s/COMAKE %(comakefile)s'%(locals())
            else:
                command='cd %(workroot)s;svn export %(trunk)s/COMAKE -r %(revision)s %(comakefile)s'%(locals())
        elif(self._scm.IsTagBranch(codetag)):
            if(revision==''):
                command='cd %(workroot)s;svn export %(branches)s%(codetag)s/COMAKE %(comakefile)s'%(locals())
            else:
                command='cd %(workroot)s;svn export %(branches)s%(codetag)s/COMAKE -r %(revision)s %(comakefile)s'%(locals())
        else:
            command='cd %(workroot)s;svn export %(tags)s%(codetag)s/COMAKE %(comakefile)s'%(locals())
        return command

    def ScmCheckoutCommand(self,cvspath,codetag,revision,force=False):
        (trunk,branches,tags)=self._GetSVNURLs(cvspath)
        if(not force):
            if(self._scm.IsTagTrunk(codetag)):
                command='svn co %(trunk)s -r %(revision)s %(cvspath)s'%(locals())
            elif(self._scm.IsTagBranch(codetag)):
                command='svn co %(branches)s%(codetag)s -r %(revision)s %(cvspath)s'%(locals())
            else:
                command='svn co %(tags)s%(codetag)s %(cvspath)s'%(locals())
        else:
            if(self._scm.IsTagTrunk(codetag)):
                command='rm -rf %(cvspath)s;svn co %(trunk)s -r %(revision)s %(cvspath)s'%(locals())
            elif(self._scm.IsTagBranch(codetag)):
                command='rm -rf %(cvspath)s;svn co %(branches)s%(codetag)s -r %(revision)s %(cvspath)s'%(locals())
            else:
                command='rm -rf %(cvspath)s;svn co %(tags)s%(codetag)s %(cvspath)s'%(locals())
        return command

    def _RemoveCommand(self,filelist):
        length = len(filelist)
        cmdlist=[]
        # remove 10 files each time
        for i in range(0, length, 10):
            if i + 10 >= length:
                end = length
            else:
                end = i + 10
            partfiles=' '.join(filelist[i:end])
            cmdlist.append("rm -rf %s"%partfiles)
        return '&&'.join(cmdlist)

    def _RemoveTemps(self,cfg):
        if(self._no_revert):
            return
        func_name='[Action:_RemoveTemps]'
        has_diff_exists=self.HasDiffExists(cfg)
        if(has_diff_exists):
            self._BackupModif(cfg)
        basepath=cfg.BasePath(self._env)
        command='cd %(basepath)s;svn st --no-ignore --xml'%(locals())
        (status,output,err)=self._log.LogDebugWithCC(
            '%s[cmd:%s]'%(func_name,command),
            command,
            2)
        if(status):
            self._log.LogFatal('%s[cmd:%s][status:%d][err:%s]'%(func_name,
                                                                command,
                                                                status,
                                                                err))
        try:
            dom=parseString(output)
            entries=dom.getElementsByTagName('entry')
            temp_file_list=[]
            for entry in entries:
                xfile=entry.getAttribute('path')
                item=entry.getElementsByTagName('wc-status')[0].getAttribute('item')
                if(item=='unversioned' or item=='ignored'):
                    if xfile.startswith('build_submitter.patch'):
                        self._log.LogWarning('Enable no-revert mode as found build_submitter.patch* under %s'%basepath)
                        self.SetNoRevert(True)
                        return
                    temp_file_list.append(xfile)
        except Exception,e:
            self._log.LogFatal('%s[Exception:%s]'%(func_name,e))

        if temp_file_list!=[]:
            remove_cmd=self._RemoveCommand(temp_file_list)
            command='cd %(basepath)s;%(remove_cmd)s'%(locals())
            (status,_,err)=self._log.LogNoticeWithCC(

                    '%s[cmd:%s]'%(func_name,
                              Function.ShortenWord(command)),
                    command)
            if(status):
                self._log.LogFatal('%s[cmd:%s][status:%d][err:%s]'%(func_name,
                                                                command,
                                                                status,
                                                                err))

    def HasDiffExists(self,cfg):
        func_name='[Action:HasDiffExists]'
        basepath=cfg.BasePath(self._env)
        command='cd %(basepath)s;svn st --xml'%(locals())
        (status,output,err)=self._log.LogDebugWithCC(
            '%s[cmd:%s]'%(func_name,command),
            command,
            2)  
        if(status):
            self._log.LogFatal('%s[cmd:%s][status:%d][err:%s]'%(func_name,
                                                                command,
                                                                status,
                                                                err))
        has_diff_exists=False
        try:
            dom=parseString(output)
            entries=dom.getElementsByTagName('entry')
            for entry in entries:
                xfile=entry.getAttribute('path')
                item=entry.getElementsByTagName('wc-status')[0].getAttribute('item')
                if(item=='added' or item=='modified'
                    or item=='replaced' or item=='conflicted'
                    or item=='obstructed' or item=='deleted'):
                    has_diff_exists=True
                    break
        except Exception,e:
            self._log.LogFatal('%s[Exception:%s]'%(func_name,e))
        return has_diff_exists

    def NeedUpdated(self,cfg):
        func_name='[Action:Update]'
        (basepath,cvspath,codetag)=(cfg.BasePath(self._env),
                                    cfg.CVSPath(),
                                    cfg.CodeTag())
        (localtag,localrev)=self.GetTagAndRevision(cvspath)
    #    (localtag,localrev_HEAD)=self.GetTagAndHeadRevision(cvspath)
        #NOTICE(zhangyan04):这个地方我们需要检查一下
        #本地代码的Tag是否和我们要使用的Tag相同.
        self._log.LogNotice(
            '%s[cvspath:%s][local:%s][revision:%s][code:%s][HEAD:%s]'%(
                func_name,
                cvspath,
                localtag,
                localrev,
                codetag,
                cfg.Revision()))
        
        #1.如果tag不同
        #2.如果tag相同但revision不同
        if localtag!=codetag:
            return True
        if localtag==BaiduSVNCodeSystem.UNKNOWN:
            return True
        if localrev!=cfg.Revision():
            return True

        #tag相同，revision也相同，但是上次更新没有成功...
        return not self.TagExists(cfg)
            
    def _GetTagAndRevisionByCommandInXML(self,command,maxrepeat=1,do_print=False):
        """通过命令得到本地环境的TAG和REVISION"""
        func_name='[Action:_GetTagAndRevisionByCommandInXML]'
        if(maxrepeat>1):
            (status,output,err)=self.ConnectSvn(command,
                                                None,#cfg
                                                maxrepeat,
                                                False,#keep_going
                                                True,#no_verify
                                                func_name)
        elif(do_print==False):
            (status,output,err)=self._log.LogDebugWithCC(
                '%s[cmd:%s]'%(func_name,command),
                command,
                2)
        else:
            (status,output,err)=self._log.LogNoticeWithCC(
                    '%s[cmd:%s]'%(func_name,
                              Function.GreenIt(command)),
                    command)
        if(status):
            return (BaiduSVNCodeSystem.UNKNOWN,
                    BaiduSVNCodeSystem.UNKNOWN)
        try:
            dom=parseString(output)
            revision=dom.getElementsByTagName('commit')[0].getAttribute('revision')
            url=dom.getElementsByTagName('url')[0].firstChild.data
            tag=self._scm._TRUNK_TAG
            #NOTICE(zhangyan04):
            #TODO:more intelligent way.
            if(url.find(self._scm._TRUNK_TAG)==-1):
                ps=string.split(url,':')
                tag=string.split(ps[1],'/')[-1]
            return (tag,revision)
        except Exception,e:
            self._log.LogDebug('%s[Exception:%s]'%(func_name,e),2)
        return (BaiduSVNCodeSystem.UNKNOWN,
                BaiduSVNCodeSystem.UNKNOWN)

    def GetTagAndRevision(self,cvspath,query_config_root=True):
        """得到本地Tag和Revision"""
        func_name='[Action:GetTagAndRevision]'
        basepath=os.path.join(self._env.WorkRoot(),
                              cvspath)
        if(not os.path.exists(basepath)):
            self._log.LogNotice('%s[!exists:%s]'%(func_name,
                                                  basepath))
            return (BaiduSVNCodeSystem.UNKNOWN,
                    BaiduSVNCodeSystem.UNKNOWN)
        command='cd %(basepath)s;svn info --xml'%(locals())
        (tag,revision)=self._GetTagAndRevisionByCommandInXML(command)
        #NOTICE(zhangyan04):
        #这是一个非常特殊的情况.
        #如果这个目录就是通过子目录下载的话,那么实际上是没有任何CodeTag的
        #那么codetag就使用父目录的codetag.        
        if(query_config_root 
           and self._env.QueryConfigRoot(cvspath)!=cvspath):
            tag=self._env.QueryCodeTagByCVSPath(cvspath)
        return (tag,revision)

    def GetTagAndHeadRevision(self,cvspath):
        """得到本地Tag和Head Revision"""
        func_name='[Action:GetTagAndHeadRevision]'
        basepath=os.path.join(self._env.WorkRoot(),
                              cvspath)
        if(not os.path.exists(basepath)):
            self._log.LogNotice('%s[!exists:%s]'%(func_name,
                                                  basepath))
            return (BaiduSVNCodeSystem.UNKNOWN,
                    BaiduSVNCodeSystem.UNKNOWN)
        command='cd %(basepath)s;svn info -r HEAD --xml'%(locals())
        # It proves a costy command of "svn info -r HEAD". Print sth. making people feel better. 
        (tag,revision)=self._GetTagAndRevisionByCommandInXML(command,do_print=True)
        #NOTICE(zhangyan04):
        #这是一个非常特殊的情况.
        #如果这个目录就是通过子目录下载的话,那么实际上是没有任何CodeTag的
        #那么codetag就使用父目录的codetag.
        if(self._env.QueryConfigRoot(cvspath)!=cvspath):
            tag=self._env.QueryCodeTagByCVSPath(cvspath)
        return (tag,revision)
    
    def _GetRemoteRevision(self, cfg):
        (trunk,branches,tags)=self._GetSVNURLs(cfg.CVSPath())
        cvspath=cfg.CVSPath()
        codetag=cfg.CodeTag()
        if(self._scm.IsTagTrunk(codetag)):
            command='svn info %(trunk)s -r HEAD --xml'%(locals())
        elif(self._scm.IsTagBranch(codetag)):
            command='svn info %(branches)s%(codetag)s -r HEAD --xml'%(locals())
        else:
            command='svn info %(tags)s%(codetag)s -r HEAD --xml'%(locals())
        (tag,revision)=self._GetTagAndRevisionByCommandInXML(command,maxrepeat=6,do_print=True)
        basepath = cfg.BasePath(self._env)
        try:
            recordfile = self._FileForRecordRevision(basepath)
            f = open(recordfile,'w')
            f.write(revision)
            f.close()
        except:
            self._log.LogFatal("Fail to write revision info to %s"%recordfile)

    def GetRemoteRevision(self, cfg):
        func_name='[GetRemoteRevision]'
        if(cfg.Revision()!=''):
            return
        if not self.EnableParallelUpdates():
            self._GetRemoteRevision(cfg)
            self._GetRevisionFromFile(cfg)
            return
        idle=self._GetIdleThread()
        while(idle==-1):
            idle=self._GetIdleThread()

        pid = os.fork()
        if pid == 0:
            self._GetRemoteRevision(cfg)
            os._exit(0)
        elif pid == -1:
            msg='Fail to fork'
            self._log.LogFatal('%s%s'%(func_name,msg))
        else:
            self._update_tabs[idle]=(pid, cfg)
            return

    def TagExists(self,cfg):
        basepath=cfg.BasePath(self._env)
        updated_tag=os.path.join(basepath,self._UPDATED_TAG)
        return os.path.exists(updated_tag)

    def TagRemoved(self,cfg):
        basepath=cfg.BasePath(self._env)
        updated_tag=os.path.join(basepath,self._UPDATED_TAG)
        if(os.path.exists(updated_tag)):
            os.remove(updated_tag)

    def TagUpdated(self,cfg):
        basepath=cfg.BasePath(self._env)
        updated_tag=os.path.join(basepath,self._UPDATED_TAG)
        open(updated_tag,'w').close()

    def _VerifyIntegrity(self,basepath):
        # TODO: to detect incompleted or missing files from local .svn dir?
        return True

        func_name='[_VerifyIntegrity]'
        command='cd %(basepath)s&&svn st -u -q'%(locals())
        (status,output,err)=self._log.LogDebugWithCC(
            '%s[cmd:%s]'%(func_name,command),
            command,
            2)
        if(status):
            self._log.LogFatal('%s[cmd:%s][status:%d][err:%s]'%(func_name,
                                                                command,
                                                                status,
                                                                err))
        try:
            lines=output.split('\n')
            for l in lines:
                if len(l) >= 9 and l[8] == '*':
                    return False
        except Exception,e:
            self._log.LogFatal('%s[Exception:%s]'%(func_name,e))
        return True

    def _SecondUpdate(self,cfg,co_time):
        func_name='[_SecondUpdate]'
        up_time=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        (cvspath,basepath,revision)=(cfg.CVSPath(),
                                     cfg.BasePath(self._env),
                                     cfg.Revision())
        command='cd %(basepath)s&&svn update -r %(revision)s'%(locals())
        (status,output,err)=self._log.LogDebugWithCC(
            '%s[cmd:%s]'%(func_name,command),
            command,
            2)
        if(status):
            self._log.LogWarning('%s[cmd:%s][status:%d][err:%s]'%(func_name,
                                                                command,
                                                                status,
                                                                err))
            return False
        lines=output.split('\n')
        if(len(lines)>2):
             """
             self._log.LogWarning('%s[cmd:%s][output:%s]'%(func_name,
                                                            command,
                                                            output))
             """
             contents=list()
             contents.append(' CO-TIME: %s'%co_time)
             contents.append(' UP-TIME: %s'%up_time)
             (tag,_)=self.GetTagAndRevision(cvspath,query_config_root=False) 
             contents.append('SVN INFO: %s@%s:%s'%(cvspath,tag,revision))
             contents.append('      IP: %s'%socket.gethostbyname(socket.gethostname()))
             contents.append('    USER: %s'%self._GetSvnUserFromLocal())
             contents_s='\n\n'.join(contents)+'\n'
             MAIL_TO='-c scmtools-notice@baidu.com zhangquan@baidu.com'
             subject='[WARNING][comake2]SVN UPDATE MISSING FILES'
             os.system('echo -e "%s"|mail -s "%s" %s'%(contents_s,subject,MAIL_TO))
        return True

    def _GetSvnUserFromLocal(self):
        svn_conf_file='%s/.subversion/auth/svn.simple/48eed6299865c0af1dac26d1a6d79efa'%os.getenv('HOME')
        if(not os.path.exists(svn_conf_file)):
            return BaiduSVNCodeSystem.UNKNOWN
        try:
            fp=file(svn_conf_file,'r')
            lines=fp.readlines()
            fp.close()
            return lines[-2].strip()
        except:
            return BaiduSVNCodeSystem.UNKNOWN
 
    def ConnectSvn(self,command,cfg=None,maxrepeat=6,keep_going=False,no_verify=False, func_name='[Action:Update]'):
        count=0
        while True:
            curtime=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
            (status,output,err)=self._log.LogNoticeWithCC(
                    '%s[cmd:%s]'%(func_name,
                              Function.GreenIt(command)),
                    command)
            if(status):
                count +=1
                if count >= maxrepeat \
                   or err.__contains__('403 Forbidden'):
                    if(not self._keep_going and not keep_going):
                        msg="%s[cmd:%s][status:%d][err:%s]"%(func_name,
                                                     command,
                                                     status,
                                                     err)
                        self._log.LogFatal(msg)
                    return (status,output,err)
                self._log.LogWarning('svn command failed, retrying ... %d'%count)
                time.sleep(1)
                continue 
            #elif(no_verify==False and not self._VerifyIntegrity(basepath)):
            elif(no_verify==False and cfg and not self._SecondUpdate(cfg,curtime)):
                count +=1
                self._log.LogWarning('fail to verify sources integrity, retrying ... %d'%count)
                time.sleep(1)
                continue
            break
        return (0,output,err)

    def _Update(self,cfg):
        func_name='[Action:Update]'
        basepath=cfg.BasePath(self._env)
        cvspath=cfg.CVSPath()
        self._env.ClearCachedTag(cfg)
        #如果目录不存在的话,那么就需要强制下载某个4位版本/主干/分支.
        if not os.path.exists(basepath) \
           or not os.path.exists(os.path.join(basepath, ".svn")):
            
            if self._env.CacheHit(cfg):
                return
            if os.system("rm -rf %s"%basepath):
                self._log.LogFatal("Fail to remove %s"%basepath)  
            command=self.CheckoutCommand(cfg)
            (status,_,_)=self.ConnectSvn(command,cfg)
            if status==0:
                self.TagUpdated(cfg)
            return 
        
        if not self.NeedUpdated(cfg):
            return

        if self._env.CacheHit(cfg):
            return

        self.TagRemoved(cfg)
        self._RemoveTemps(cfg)

        command=self.SwitchCommand(cfg)
        (status,_,_)=self.ConnectSvn(command,cfg,maxrepeat=1,keep_going=True)
        if(status):
            if(self._no_revert):
                self._log.LogFatal('在norevert模式下更新代码失败！')
            self._log.LogWarning('更新代码失败，继续ing ...')
            command=self.SwitchCommand(cfg,force=True)
            (status,_,_)=self.ConnectSvn(command,cfg)
            if status==0:
                self.TagUpdated(cfg)
                self._log.LogNotice('更新代码成功！')
            return
            
        self.TagUpdated(cfg)

    def Update(self,cfg):
        func_name='[Action:Update]'
        basepath=cfg.BasePath(self._env)
        cvspath=cfg.CVSPath()
        #NOTICE(zhangyan04)如果这个属于其他模块子目录的话.那么也不会发生更新.
        #或者是当前目录的子目录,是不会发生更新的.
        if(self._env.QueryConfigRoot(cvspath)!=cvspath or
           os.path.abspath(basepath)==os.path.abspath(os.getcwd()) or
           os.path.abspath(basepath).startswith(
                '%s/'%(os.path.abspath(os.getcwd())))):
            self._log.LogNotice('%s[ignore:%s]'%(func_name,cvspath))
            return

        if not self.EnableParallelUpdates():
            self._Update(cfg)
            return
        idle=self._GetIdleThread() 
        while(idle==-1):
            idle=self._GetIdleThread() 

        if(idle!=-1):
            pid = os.fork()
            if pid == 0:
                #self._env.set_signal_handler()
                self._Update(cfg)
                os._exit(0)
            elif pid == -1:
                msg='Fail to fork'
                self._log.LogFatal('%s%s'%(func_name,msg))
            else:
                self._update_tabs[idle] = (pid, None)
                return
        else:
            self._Update(cfg)
            return
 
