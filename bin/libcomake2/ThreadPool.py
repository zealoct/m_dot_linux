#!/usr/bin/env python
#coding:gbk
#Copyright (c) Baidu.com, Inc. All Rights Reserved 
#author:zhangyan04(@baidu.com)

import threading

class ThreadPool(object):
    def __init__(self):
        self._pool=[]
        self._limit=1
    
    def SetLimit(self,limit):
        self._limit=limit
        
    def Append(self,func,args=(),kwargs={}):
        t=threading.Thread(target=func,
                           args=args,
                           kwargs=kwargs)
        self._pool.append(t)

    def Run(self):
        v=[]
        for x in self._pool:
            v.append(x)
            if(len(v)==self._limit):
                for y in v:
                    y.start()
                for y in v:
                    y.join()
                v=[]
        for y in v:
            y.start()
        for y in v:
            y.join()

    def Clear(self):
        self._pool=[]
