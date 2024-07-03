#!/usr/bin/env python
#coding:utf-8
#Copyright (c) Baidu.com, Inc. All Rights Reserved 
#author:zhangyan04(@baidu.com)

import string
import copy

import Function

class TagVector(object):
    def __init__(self):
        self._v=[]
    def AddV(self,v):
        self._v.extend(string.split(v))
    def AddVs(self,vs):
        for v in vs:
            self._v.extend(string.split(v))
    def AddSV(self,v):
        self._v.append(v)
    def AddSVs(self,vs):
        for v in vs:
            self._v.append(v)
    def V(self):
        return self._v
    def __add__(self,v):
        newtag=copy.copy(self)
        newtag._v=copy.copy(self._v)
        newtag._v.extend(v._v)
        return newtag
    def __sub__(self,v):
        newtag=copy.copy(self)
        newv=Function.Exclude(newtag._v,v._v)
        newtag._v=newv
        return newtag

class TagScalar(object):
    def __init__(self):
        pass
    def SetV(self,v):
        self._v=v
    def V(self):
        return self._v
    
class TagCppFlags(TagVector):
    def __init__(self):
        TagVector.__init__(self)

class TagCFlags(TagVector):
    def __init__(self):
        TagVector.__init__(self)

class TagCxxFlags(TagVector):
    def __init__(self):
        TagVector.__init__(self)

class TagIncludePaths(TagVector):
    def __init__(self):
        TagVector.__init__(self)

class TagLibraries(TagVector):
    def __init__(self):
        TagVector.__init__(self)

class TagLinkFlags(TagVector):
    def __init__(self):
        TagVector.__init__(self)

class TagIdlFlags(TagVector):
    def __init__(self):
        TagVector.__init__(self)

class TagUbRpcFlags(TagVector):
    def __init__(self):
        TagVector.__init__(self)

class TagProtoFlags(TagVector):
    def __init__(self):
        TagVector.__init__(self)

class TagHeaderFiles(TagVector):
    def __init__(self):
        TagVector.__init__(self)

class TagShellCommands(TagVector):
    def __init__(self):
        TagVector.__init__(self)

class TagCleanCommands(TagVector):
    def __init__(self):
        TagVector.__init__(self)

class TagCleanFiles(TagVector):
    def __init__(self):
        TagVector.__init__(self)
        
class TagPrefixes(TagVector):
    def __init__(self):
        TagVector.__init__(self)

class TagSelectConfigs(TagVector):
    def __init__(self):
        TagVector.__init__(self)

class TagSkipConfigs(TagVector):
    def __init__(self):
        TagVector.__init__(self)

class TagSources(TagVector):
    def __init__(self):
        TagVector.__init__(self)
        
class TagCCPDriver(TagScalar):
    def __init__(self):
        TagScalar.__init__(self)
        
class TagCCPFlags(TagVector):
    def __init__(self):
        TagVector.__init__(self)
        
class TagCCPUseIncPaths(TagScalar):
    def __init__(self):
        TagScalar.__init__(self)
        
class TagOutputPath(TagScalar):
    def __init__(self):
        TagScalar.__init__(self)

class TagHeaderOutputPath(TagScalar):
    def __init__(self):
        TagScalar.__init__(self)

class TagPhonyMode(TagScalar):
    def __init__(self):
        TagScalar.__init__(self)        

class TagFileMode(TagScalar):
    def __init__(self):
        TagScalar.__init__(self)
    
class TagUseMcy(TagScalar):
    def __init__(self):
        TagScalar.__init__(self)

class TagUseUbrpcgen(TagScalar):
    def __init__(self):
        TagScalar.__init__(self)

class TagDisableBuild(TagScalar):
    def __init__(self):
        TagScalar.__init__(self)

class TagBuildCmd(TagScalar):
    def __init__(self):
        TagScalar.__init__(self)

class TagLinkDepsFlags(TagScalar):
    def __init__(self):
        TagScalar.__init__(self)

class TagWholeArchiveLibs(TagVector):
    def __init__(self):
        TagVector.__init__(self)

class TagLinkLibs(TagVector):
    def __init__(self):
        TagVector.__init__(self)

