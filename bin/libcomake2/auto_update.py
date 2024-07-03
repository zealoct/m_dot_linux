#!/usr/bin/env python
#coding:gbk
#Copyright (c) Baidu.com, Inc. All Rights Reserved 
#author:zhangyan04(@baidu.com)

"""
更新部分.这个应该单独作为程序执行.不然很难解决权限问题.
使用的脚本方式必须切换到这个目录下面,单独执行auto_update.py.

更新的方式采用拉的方式来完成,到某个固定的地方取东西.而那个地方每天都会尝试去
ftp下载更新的版本,拿下来之后make一下就OK了.不过必须确保版本比当前的新.
"""

#这是一个单独的程序.

import os
import sys
import shutil
import commands
import urllib2

def LogDebug(msg):
    print "[DEBUG]%s"%msg
    
def LogNotice(msg):
    print "[NOTICE]%s"%msg

def LogError(msg):
    print "[ERROR]%s"%msg
    sys.exit(1)

class Update(object):
    def __init__(self):
        #使用环境变量来完成更新.
        #效果和指定参数是一样的.
        if('COMAKE2_LATEST_RELEASE_PACKAGE_LOCATION' in os.environ):
            self._package_location=os.environ['COMAKE2_LATEST_RELEASE_PACKAGE_LOCATION']            
        else:
            self._package_location='ftp://getprod:getprod@product.scm.baidu.com/data/prod-64/scm/ci-tools/latest/comake'
        #在同一个目录下面存在一个COMAKE.VERSION文件.
        #这个文件就可以用来比较版本的不同了.:).
        self._package_version_file='%s/libcomake2/COMAKE.VERSION'%self._package_location

    def PackageLocation(self):
        return self._package_location
    def PackageVersionFile(self):
        return self._package_version_file
    
    def GetRemoteVersion(self):
        """得到远程的版本号"""
        func_name="[Action:GetRemoteVersion][location:%s]"%(self._package_version_file)
        #LogNotice('%s'%(func_name))
        try:
            #使用urllib2去读取版本号.
            f=urllib2.urlopen(self._package_version_file)
            version=f.read().strip()
            f.close()
        except Exception,e:
            msg="%s[Exception:%s]"%(func_name,e)
            LogDebug(msg)
            #远程版本非常低.不发生更新.
            version=''
        return version

    def CompareVersion(self,v1,v2):
        return v1==v2

    def GetLocalVersion(self):
        return open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     'COMAKE.VERSION')).read().strip()
    
    def Action(self):
        """开始进行更新
        1.首先下载远程的版本号,并且和自己版本好对比
        2.然后把文件下载到本地然后解压并且安装[这里需要考虑目录权限]"""
        func_name="[Action:Action]"
        #如果本地更新的话,那么就不更新.
        lv=self.GetLocalVersion()
        rv=self.GetRemoteVersion()
        #需要打印一下版本好信息.
        LogNotice("%s[local:%s][remote:%s]"%(func_name,lv,rv))
        if(self.CompareVersion(lv,rv)):
            LogNotice("No need to update comake.")
            return 

        #这样限制了目录存放方式
        #比如是comake/libcomake2/__file__这样来.
        #但是通常应该不是问题.
        top_comake_dir=os.path.abspath(os.path.join(__file__,'..','..','..'))
        sub_comake_dir=os.path.abspath(os.path.join(__file__,'..','..'))
        cwd=os.getcwd()
        
        #切换到这个目录下载内容.
        LogNotice("%s[chdir:%s]"%(func_name,top_comake_dir))
        os.chdir(top_comake_dir)
        command="wget '%s' -q -r -nH --cut-dirs=5 --preserve-permissions"%(self._package_location)
        LogNotice("%s[wget comake from product.scm.baidu.com ...]"%(func_name))
        (status,output)=commands.getstatusoutput(command)
        if(status):            
            msg="%s[status:%d][cmd:%s][output:%s]"%(func_name,status,command,output)
            LogError(msg)
            return 
        
        #更新完毕.
        #How about comake installed under <path>/comake2/? move all files to installdir.
        inst_dir=os.path.basename(sub_comake_dir)
        if(inst_dir!='comake'):
            os.system('cp -frp %s/comake/* %s/'%(top_comake_dir,sub_comake_dir))
            shutil.rmtree('%s/comake'%top_comake_dir)
        os.chdir(sub_comake_dir)
        new_lv=os.popen('cat libcomake2/COMAKE.VERSION').read().strip()
        if(new_lv==rv):
            LogNotice("Update comake to version %s ok!"%rv)
        else:
            LogError("Update failed (local: %s, remote: %s), please verify it"%(new_lv,rv))
        os.chdir(cwd)
        return 

def main():
    update=Update()
    update.Action()
    
if __name__=='__main__':
    main()

