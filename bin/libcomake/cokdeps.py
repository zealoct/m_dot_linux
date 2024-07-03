#!/usr/bin/env python
# -*- coding: gb18030 -*- 

import re
import commands
import sys
import os
import string
import time

sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/libcomake/");
import kws
import cokut
import cokscm

#depsfile = kws.DEPSFILE+".cpp"

class cokdeps:
	pass

	def __init__(self):
		self.dict = {};
		self.workroot = "";
		self.module = "";
		self.depsfile = "";
		self.prj = "";
		self.prjname = "comake.prj";

	def gettpl(self, tpl):
		fn = os.path.dirname(os.path.realpath(__file__)) + "/" + tpl;
		fp = open(fn);
		ret = fp.read();
		fp.close();
		return ret;

	def genautogencpp(self, deplst):
		if os.path.exists(self.depsfile):
			os.system("cp " + self.depsfile + " ." + self.depsfile + ".bk");

		if deplst:
			depstxt = self.gettpl("auto_gen.cpp").replace(
					"__$MODULE_LOWER$__", self.module.lower()).replace(
							"__$MODULE_UPPER$__", self.module.upper());
			depsinr = self.gettpl("auto_gen_inner.cpp");
			inner = "";
			eitdict = {};
			for l in deplst:
				mod = l.split()[0];
				if mod.rfind("/") > -1:
					mod = mod[mod.rfind("/")+1:];
					if mod.lower() not in eitdict:
						inner += depsinr.replace("__$MODULE_LOWER$__", mod.lower()).replace(
								"__$MODULE_UPPER$__", mod.upper()).replace("__$LIB$__", l);
			depstxt =  depstxt.replace("__$INNER_FILE$__", inner);

			depsfp = open(self.depsfile, "w");
			depsfp.write(depstxt);
			depsfp.close();

	def buidepsdic(self, lst, add, sub, now):
		for x in lst:
			if not x:
				continue;
			if x[0] == '-':
				n = x[1:].strip();
				sub[n.split()[0]] = n.split()[1];
			elif x[0] == '+':
				n = x[1:].strip();
				add[n.split()[0]] = n.split()[1];
				c = 2;
				while c < len(n.split()):
					add[n.split()[0]] += "\t" + n.split()[c];
					c = c + 1;
			else:
				n = x.strip();
				now[n.split()[0]] = n.split()[1];

	def gendepsfile(self, deplst):
		deps = self.prjname[:self.prjname.rfind(".")] + ".deps";
		old = [];
		if os.path.exists(deps):
			fp = open(deps);
			old = fp.read().split("\n");
			fp.close();
		elif not deplst:
			return deplst;
		oldadd = {};
		oldsub = {};
		oldnow = {};
		self.buidepsdic(old, oldadd, oldsub, oldnow);
		newnow = {};
		self.buidepsdic(deplst, {}, {}, newnow);

		gen = [];
		lst = [];
		for x in deplst:
			key = x.strip().split()[0];
			if key in oldsub:
				gen.append("-\t"+x);
			elif key in oldadd:
				gen.append("+\t"+key+"\t"+oldadd[key]);
				lst.append(key + "\t" + oldadd[key]);
			else:
				gen.append(x);
				lst.append(x);
		for x in oldadd:
			if x not in newnow:
				gen.append("+\t"+x+"\t"+oldadd[x]);
				lst.append(x+"\t"+oldadd[x]);

		fp = open(deps, "w");
		fp.write("\n".join(gen));
		fp.close();

		kws.debug_log(lst);

		return lst;

	def cc(self, prj):
		deplib = {};
		self.prj = prj;
		self.workroot = prj.root.dict["WORKROOT"][0];
		config = [];
		for x in prj.root.dict[kws.CONFIG]:
			if x not in kws.CFGSKIP:
				config.append(x);
		self.module = "".join(prj.root.dict["MODULENAME"]);
		self.depsfile = kws.AUTOGEN + ".cpp";
		for x in config:
			reg = "([^()]+)\(?([0-9\.]+)?\)?";
			m = re.match(reg, x);
			key = x;
			ver = "";
			if m is not None:
				if m.group(1):
					key = m.group(1);
				if m.group(2):
					ver = m.group(2);

			if key[:4] == "lib2":
				deplib["lib2" + key[key.find("/"):]] = ver;
				deplib["lib2-64" + key[key.find("/"):]] = ver;
			elif key[:5] == "third":
				deplib["third" + key[key.find("/"):]] = ver;
				deplib["third-64" + key[key.find("/"):]] = ver;
			else:
				deplib[key] = ver;

		cokscm.scmtools().download();
		deplst = cokscm.scmtools().getalldeps(deplib);

		#self.genautogencpp(deplst);

		deplst = self.gendepsfile(deplst);

		if (kws.CHECKOUT == True):
			self.auto_load(deplst);

		parret = self.parser_deps(deplst);

		self.dict["DEP_INCPATH"] = [];
		self.dict["DEP_LDFLAGS"] = [];
		self.dict["DEP_LDLIBS"] = [];

		for x in parret["inc"]:
			self.dict["DEP_INCPATH"].append(x);
		for x in parret["ldinc"]:
			self.dict["DEP_LDFLAGS"].append(x);
		for x in parret["ldlibs"]:
			self.dict["DEP_LDLIBS"].append("-l"+x);
		for x in parret["ldfulllibs"]:
			self.dict["DEP_LDLIBS"].append(x);

	def auto_load (self, deplst):
		for x in reversed(deplst):
			tlib = x.split()[0];
			tpdbl = x.split()[1];
			cvscmd = "cd " + self.workroot + ";";
			cvscmd += "if [ -e \""+tlib+"\" ];then ";
			backdir = "~/.backup.comake/" + os.path.dirname(tlib);
			cvscmd += "mkdir -p " + backdir + ";";
			cvscmd += "mv "+tlib+ " " + backdir + "/" + time.ctime().replace(" ", "_")+";";
			cvscmd += "fi;"
			if tpdbl == "NEW":
				cvscmd += "cs co " + tlib + ";";
			else:
				cvscmd += "cs co -r " + tpdbl + " " + tlib + ";";
			cvscmd += "if [ -e \""+tlib+"\" ];then ";
			cvscmd += "echo \"checkout "+tlib+" ok\";";
			cvscmd += "else ";
			cvscmd += "cs co " + tlib +";"
			cvscmd += "fi;"
			cvscmd += "make -j 4 -C " + tlib;
			kws.debug_log(cvscmd);
			print cvscmd;
			os.system(cvscmd);
			#print cvscmd;
	
	def parser_deps (self, deplst):
		inc = {};
		incmap = {};
		ldinc = {};
		ldincmap = {};
		ldlibsmap = {};
		ldlibs = [];
		ldfullinmap = {};
		ldfulllibs = [];
		for x in deplst:
			kws.debug_log(x);
			xlib = "";
			if len(x.split()) > 2:
				xlib=x.split()[2];
			kws.debug_log(xlib);
			x = x.split()[0];
			base = self.workroot + "/";
			fbase = "$("+kws.WORKROOT+")/";
			d = x;
			if x[:4] == 'lib2':
				d = "$(lib2)" + x[x.find("/"):];
			elif x[:5] == 'third':
				d = "$(third)" + x[x.find("/"):];
			#print "#######-----" + base + x;
			for y in ["/output/", "/"]:
				if os.path.exists(base + x + y):
					#print "######----------" + base + x + y;
					for z in ["/include/", "/"]:
						if os.path.exists(base + x + y + z):
							inc[fbase + d + y + z] = "";
							break;
					for z in ["/lib/", "/"]:
						if os.path.exists(base + x + y + z):
							ldinc[fbase + d + y + z] = "";
							if xlib:
								cmd="";
								for xx  in xlib.split("||"):
									cmd = cmd + "find " + base + x + y + z + " -name \""+xx+"\";";
							else:
								if x in ["lib2/bsl", "lib2-64/bsl"]:
									cmd = "find " + base + x + y + z + " -name \"libbsl.a\";";
								elif x in ["public/ub"]:
									cmd = "find " + base + x + y + z + " -name \"libub.a\";";
								else:
									cmd = "find " + base + x + y + z + " -name \"lib*.a\";";
									cmd += "find " + base + x + y + z + " -name \"lib*.so\";"
							kws.debug_log(cmd + "---" + xlib);
							for l in os.popen(cmd).read().split():
								n = os.path.basename(l);
								#print l;
								#print n[-2:];
								if n[-2:] == "so":
									l = n[3:-3];
									#print l;
								else:
									l = n[3:-2];

								if l not in ldlibsmap:
									ldlibsmap[l] = "";
									ldlibs.append(l);
								#if l not in ldfullinmap:
								#	ldfullinmap[l] = "";
								#	ldfulllibs.append(l);
							break;
					break;
		ret = {};
		ret["inc"] = inc;
		ret["ldinc"] = ldinc;
		ret["ldlibs"] = ldlibs;
		ret["ldfulllibs"] = ldfulllibs;

		#print ret;
		return ret;

