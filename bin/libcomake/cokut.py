#!/usr/bin/env python
import re
import commands
import sys
import os
import string
import time

sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/libcomake/");
import kws

def get_workroot():
	if kws.WORKROOT in os.environ:
		en = [];
		for x in os.environ[kws.WORKROOT].split('/'):
			if x:
				en.append(x);
		gn = [];
		for x in os.getcwd().split('/'):
			if x:
				gn.append(x);
		if '/'.join(gn).find('/'.join(en)) != 0:
			return os.environ[kws.WORKROOT];
		cnt = len(gn) - len(en);
		if cnt == 0:
			return '.';
		wp = "";
		while cnt > 0:
			wp = wp + "../";
			cnt = cnt - 1;
		return wp;


	lst = os.getcwd().split('/');
	start = '';
	dep = 2;
	for i in range(0, len(lst), 1):
		if lst[i]:
			start = start + '/' + lst[i];
		if i < 3:
			continue;
		if os.path.exists(start+"/CVS") and os.path.exists(start + "/CVS/Root"):
			dep = i-1;
			break;
	
	workrootpath = "";
	scnt =  os.getcwd().count("/");
	while scnt > dep:
		scnt = scnt - 1;
		workrootpath += "../";
	if not workrootpath:
		workrootpath = "./";
	return workrootpath;

def xfindf(base, hz):
	cmd = "find " + base + " -name \"" + hz + "\"";
	lst = os.popen(cmd).read().split();
	ret = [];
	for x in lst:
		if x[:2] == "./":
			i=2;
			while x[i] == '/':
				i = i+1;
			ret.append(x[i:]);
	return ret;

if __name__ == "__main__":
	print xfindf(".", "*");
