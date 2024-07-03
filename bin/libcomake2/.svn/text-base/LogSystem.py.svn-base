#!/usr/bin/env python
#coding:gbk
#Copyright (c) Baidu.com, Inc. All Rights Reserved 
#author:zhangyan04(@baidu.com)

import sys
import threading
import Function

class TerminalWriter(object):
    def __init__(self):
        self._lock=threading.Lock()
    def write(self,s):
        #self._lock.acquire()
        sys.__stderr__.write(s)
        #self._lock.release()
        
class TerminalLogSystem(object):
    def __init__(self,
                 notice,
                 debug,
                 warning,
                 fatal):
        self._notice=notice
        self._debug=debug
        self._warning=warning
        self._fatal=fatal
        self._quiet=False
        self._debug_level=0
        self._tw=TerminalWriter()      
        self._parallel_mode=False

    def SetQuiet(self):
        self._quiet=True
    def IncDebugLevel(self):
        self._debug_level+=1
    def SetParallelMode(self,k):
        self._parallel_mode=k
        
    def LogNotice(self,v):
        if(not self._quiet):            
            self._tw.write("[%s]%s\n"%(
                    self._notice,
                    v))

    def LogNoticeWithCC(self,v,cmd,noerror=False):
        if(self._parallel_mode):
            return self._LogNoticeWithCCinParallel(v,cmd,noerror)
        if(not self._quiet):
            self._tw.write("[%s]%s[status:"%(
                    self._notice,
                    v))
        (status,out,err)=Function.call_command(cmd)
        if(not self._quiet):
            self._tw.write("%d]"%(status))
            if(err and not noerror):
                self._tw.write("[err:%s]\n"%(err))
            else:
                self._tw.write("\n")
        return (status,out,err)

    def _LogNoticeWithCCinParallel(self,v,cmd,noerror):
        if(not self._quiet):
            self._tw.write("[%s]%s\n"%(
                    self._notice,
                    v))
        (status,out,err)=Function.call_command(cmd)
        if(not self._quiet):
            if(status==0 and err and not noerror):
                self._tw.write("[%s]%s[status:0][err:%s]\n"%(
                    self._debug,
                    v,err))
        return (status,out,err)

    def LogDebug(self,v,trigger=1):
        if(not self._quiet and
           self._debug_level>=trigger):
            self._tw.write("[%s]%s\n"%(
                    self._debug,
                    v))
    
    def LogDebugWithCC(self,v,cmd,trigger=1):
        if(not self._quiet and
           self._debug_level>=trigger):
            self._tw.write("[%s]%s[status:"%(
                    self._debug,
                    v))
        (status,out,err)=Function.call_command(cmd)
        if(not self._quiet and
           self._debug_level>=trigger):
            self._tw.write("%d]"%(status))
            if(err):
                self._tw.write("[err:%s]\n"%(err))
            else:
                self._tw.write("\n")
        return (status,out,err)

    def LogFatal(self,v):
        # Traceback is not so welcome
        #raise Exception("[%s]%s"%(self._fatal,v))
        self._tw.write("Exception: [%s]%s\n"%(self._fatal,v))
        sys.exit(1)
    
    def LogWarning(self,v):
        if(not self._quiet):
            self._tw.write("[%s]%s\n"%(
                    self._warning,v))

LOGSYS=TerminalLogSystem(
            Function.GreenIt('NOTICE'),
            Function.GreenIt('DEBUG'),
            Function.RedIt('WARNING'),
            Function.RedIt('FATAL'))

def GetCurrent():
    global LOGSYS
    return LOGSYS
