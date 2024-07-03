#!/usr/bin/python
# -*- coding: gb18030 -*- 

import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/libcomake/");

import kws;

#从scm下载数据
class scmtools:
	pass
	_shell = "curl -s \""+ kws.SCMPFURL +"\"";
        
	_tool = ".scmtools.cok.tmp"

	def download(self):
		os.system(self._shell + " > " + self._tool);

	def getdep(self, cvspath, ver=""):
		args = " -p=" + cvspath + " -do=info ";
		if ver:
			args += " -v=" + ver;
		args += " -y";
		percmd = "perl " + self._tool + args; 
		#os.system("perl " + self._tool + args);
		kws.debug_log(percmd);
		
		res = os.popen(percmd).read();
		status = 0;
		vec = [];
		for x in res.split("\n"):
			y = x.split();
			if y:
				if y[0] == "cvspath":
					status = 1;
				elif y[0][0:2] == "**":
					break;
				elif status == 1:
					if x[0] != '{':
						vec.append(x);
					else:
						vec.append(x[3:]);
		if status != 1:
			return [];
		return vec;

	#vset是除重用的，标识模块是否已经被扫描过，动态规划的一部分
	#vmap 记录每个模块的依赖库
	#cvsp 是当前要扫描的模块
	#ver 是当前模块的版本
	#vverm 记录每个模块目前的版本信息
	def _getfulldepset(self, vset, vmap, cvsp, ver, vverm):
		#已经存在，结束
		cvspath = cvsp.rstrip("//");
		if cvspath in vset:
			return;
		#try to get cvspath, flag it i get it;
		vset.add(cvspath);
		#获取这个模块的所有编译依赖
		dep = self.getdep(cvspath, ver);

		#获取不到，假设这个什么都不依赖
		if not dep:
			vmap[cvspath] = set();
			vverm[cvspath] = ver;
			print "--[warning] can't check the module " + cvspath + "(" + ver + ")";
			return;

		#递归扫描这个编译依赖下的所有依赖
		depset = set();
		for x in dep:
			y = x.split();
			#将这个编译依赖放入set中
			depset.add(y[0]);
			#如果模块的版本信息已经存在，且当前的版本信息比指定的要新，或者版本信息不存在，更新版本信息
			if (y[0] in vverm and vverm[y[0]] < y[1]) or (y[0] not in vverm) :
				#lib to version map
				vverm[y[0]] = y[1];

			#递归获取这个模块的编译依赖
			self._getfulldepset(vset, vmap, y[0], y[1], vverm);

		#remove your self
		if cvspath in depset:
			depset.remove(cvspath);

		#生成这个模块对应的所有编译依赖，剔除自己
		vmap[cvspath] = depset;
	
	#拓扑排序
	def sortdep(self, vmap):
		lst=[];
		cnt = len(vmap);
		flag = 0;
		
		while cnt > 0:
			delst = [];
			flag = 1;
			for k in vmap:
				if not vmap[k]:
					lst.insert(0, k);
					delst.append(k);
					cnt = cnt - 1;
					flag  = 0;

			if flag == 1:
				print vmap;
				print "error can't sort vmap";
				break;

			for l in delst:
				del vmap[l];
				for k in vmap:
					if l in vmap[k]:
						vmap[k].remove(l);

		if flag == 1:
			for k in vmap:
				lst.append(k);
		return lst;

	def addver (self, olst, vvmer):
		lst = [];
		for x in olst:
			if vvmer[x].strip() in ["NEW", '']:
				lst.append(x + "    " + "NEW");
			else:
				#lst.append(x + "    " + "NEW");
				lst.append(x + "    " + os.path.basename(x) +"_"+ vvmer[x].replace(".", "-")+"_PD_BL");
		return lst;

	def getfulldep(self, cvspath, ver=""):
		vset=set();
		vmap={};
		vverm={};
		self._getfulldepset(vset, vmap, cvspath, ver, vverm);
		#return self.sortdep(vmap);
		return self.addver(self.sortdep(vmap), vverm);

	def getfulldeps(self, pm):
		vset=set();
		vmap={};
		vverm={}
		for p in pm:
			self._getfulldepset(vset, vmap, p, pm[p], vverm);
		#return self.sortdep(vmap);
		return self.addver(self.sortdep(vmap), vverm);


	def getalldeps (self, pm):
		vset=set();
		vmap={};
		vverm={}
		for p in pm:
			self._getfulldepset(vset, vmap, p, pm[p], vverm);

		for p in pm:
			if pm[p] and p in vverm:
				vverm[p] = pm[p];

		#copy vmap
		nvmap = {};
		for x in vmap:
			nvmap[x] = vmap[x];

		lst = self.addver(self.sortdep(vmap), vverm);

		for p in pm:
			if p not in nvmap:
				if not pm[p]:
					lst.insert(0, p + "    NEW");
				else:
					lst.insert(0, p + "   " + os.path.basename(p) + "_" + pm[p].replace(".", "-") + "_PD_BL");
		return lst;

	def test_run(self):
		self.download();
		print self.getfulldep("public/fileblock");
		#args = "";
		#for x in sys.argv[1:]:
		#	args += " " + x;
		#os.system("perl " + self._tool + args + " >/dev/null 2>&1");
		#print self.getdep("public/nshead", "1.0.0.0");
		#print self.getdep("public/ub");
		#print self.getfulldep("public/ub");
		#print self.getfulldep("app/search/ziyuan/video");
		#print self.getfulldep("com/comdb/comdb/");
		#print self.getfulldep("app/search/favo/fuser");
		#print self.getfulldep("lib2/ccode");
		#print self.getfulldep("ibase/gm/ngui/prototype");
		#vmap={"public/ub":"", "app/search/ziyuan/video":"", 
		#		"com/comdb/comdb/":"", "app/search/favo/fuser":"",
		#		"lib2/ccode":""};
		#print self.getfulldeps(vmap);
		#print self.getfulldep("app/search/ziyuan/lib");
		#print self.getfulldep("public/mcpack");
		#print self.getfulldep("lib2/bsl");
		#print self.getfulldep("public/idlcompiler");

if __name__ == "__main__":
	scmtools().test_run();
