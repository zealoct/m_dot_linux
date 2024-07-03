#!/usr/bin/env python
# -*- coding: gb18030 -*- 
import re
import commands
import sys
import os
import string
import time

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/libcomake/");
import cokparser
import cokdeps
import kws

comake_bin = os.path.dirname(os.path.realpath(__file__)) + "/../comake";

makenv = '''
WORKROOT=./
CC = gcc
CXX = g++
LEX = flex
YACC = yacc
IDLCC = $(WORKROOT)/public/idlcompiler/output/bin/mcy
RPCCC = $(WORKROOT)/public/ubrpc/output/bin/ubrpcgen
CFLAGS = -pipe -Wall -W -g -fPIC
CXXFLAGS = -pipe -Wall -W -g -fPIC
IDLFLAGS =
CPPFLAGS = 
LINK = g++
LDFLAGS =
LDLIBS = -lcrypto -lm -lpthread
COMAKE = comake
LINKFLAGS = -rdynamic
AR = ar cqs
RANLIB = 
INCPATH = .
LEXFLAGS = 
YACCFLAGS = 
LINK = g++
SOURCES = '''+kws.AUTOGEN+'''.cpp
CONFSRC = 
#DEP_INCPATH = .
#DEP_LDFLAGS = .
#DEP_LDLIBS = 
HEADERS = *.h  
SHELL = 
CONFIG =
DEPFILES = 
PHONY = 
RPCIDL =
FORCE_CLEAN =
''' + "\nMODULENAME = " + os.path.basename(os.getcwd()) + "\n"
class cokmake:
	pass
	def __init__(self):
		self.outfile = "Makefile";
		self.prjfile = "";
		pass

	def set_prjfile(self, prj):
		self.prjfile = prj;
	def set_outfile(self, out):
		self.outfile = out;

	def cc(self, tar):
		src = self.cc_tar(tar, 0);
		rpcval = "rpcidl : ";
		lst = tar.allval("RPCIDL");
		for x in lst:
			rpcval += x + " ";
		rpcval += "\n";
		for x in lst:
			rpcval += "\t $(RPCCC) $(IDLFLAGS) " + x + "\n";
			rpcval += "\t $(IDLCC) --ubrpc $(IDLFLAGS)  " + x + "\n"
		rpcval += "\n";
		rpcval += "clean_rpcidl : \n"
		for x in lst:
			rpcval += "\trm -f " + x + ".*\n";

		return src.replace("__$IDLRPC_SUPPORT$__", rpcval);

	def pjoin(self, str, lst):
		nlst = [];
		for x in lst:
			if len(x.strip()) > 0:
				nlst.append(x);
		if nlst and len("".join(nlst).strip()) > 0:
			return str+str.join(nlst);
		else:
			return "";

	def csrc(self, str):
		try:
			f = str[str.rfind(".") + 1 : ].strip();
			if f in ["c", "cc", "cpp", "cxx"]:
				#print f+"----";
				return 1;
		except:
			return 0;
		return 0;

	def ccprj(self, env={}):
		p = cokparser.cokparser();
		p.cc(makenv, env);
		fp = open(self.prjfile);
		p.cc(fp.read(), env);
		fp.close();
		return p;

	def ifdebug(self, outfile, p, env):
		if p.jdict[kws.DEBUGSCOPE]:
			t = cokparser.tarobj(p.root);
			t.type = "all";
			t.name = "debug";
			t.dict["SHELL"] = ["make -f "+outfile+".debug"];
			p.root.tarlst.append(t);
			env[kws.DEBUGSCOPE] = (1==1);
			self.run2(outfile+".debug", env);
		self.gen(outfile, p);

	def run(self):
		p = self.ccprj();
		kws.debug_log("---------------------");
		if p.jdict[kws.LINUX32] == 0 and p.jdict[kws.LINUX64] == 0:
			env = { kws.LINUX32:kws.IS_32, kws.LINUX64:kws.IS_64};
			self.ifdebug(self.outfile, p, env);
		else:
			self.genchange(p);
			env = { kws.LINUX32:(1==1), kws.LINUX64:(1==0),
					kws.DEBUGSCOPE:(1==0)};
			p = self.ccprj(env);
			self.ifdebug(self.outfile+".32", p, env);
			env = { kws.LINUX32:(1==0), kws.LINUX64:(1==1),
					kws.DEBUGSCOPE:(1==0)};
			p = self.ccprj(env);
			self.ifdebug(self.outfile+".64", p, env);

	def run2(self, outfile, env):
		p = self.ccprj(env);
		self.gen(outfile, p);

	def genchange(self, p):
		fn = os.path.dirname(os.path.realpath(__file__)) + "/change.tpl";
		fp = open (fn);
		maketpl = fp.read();
		fp.close();
		maketpl = maketpl.replace("__$outfile$__", self.outfile);
		for t in p.root.tarlst:
			if t.name not in ["debug", "clean", "output", "cov", "ccpc", "test"]:
				maketpl += "\n"+t.name+":\n\tmake "+t.name+" -f $(release)\n";
		fp2 = open(self.outfile, "w");
		fp2.write(maketpl);
		fp2.close();

	def gen(self, outfile, p):
		lst = p.root.allval("IDLSRC");
		if lst:
			existidl = 0;
			for x in p.root.allval("CONFIG"):
				if x.find("public/idlcompiler") != -1:
					existidl = 1;
					break;
			if existidl == 0:
				p.root.dict["CONFIG"].append("public/idlcompiler");

		#add marco
		dep = cokdeps.cokdeps();
		dep.prjname = self.prjfile;
		dep.cc(p);
		for key in dep.dict:
			if key not in p.root.dict:
				p.root.dict[key] = dep.dict[key];

		#replace total sources
		lst = p.root.allval("SOURCES");
		if "TOTAL_SOURCES" not in p.root.dict:
			p.root.dict["TOTAL_SOURCES"] = [];

		for x in lst:
			if x not in p.root.dict["TOTAL_SOURCES"] and self.csrc(x) == 1:
				#print "append: " + x;
				p.root.dict["TOTAL_SOURCES"].append(x);

		kws.debug_log(p.env);
		kws.debug_log(p.jdict);
		kws.debug_log(p.root);
		
		fp2 = open(outfile, "w");
		fp2.write(self.cc(p.root));
		fp2.close();

	def add_default_tar(self, tar):
		tar_dict = {};
		for t in tar.tarlst:
			tar_dict[t.name] = t;
		deflst = ["output", "clean", "ccpc", "cov"];
		for l in deflst:
			if l not in tar_dict:
				t = cokparser.tarobj(tar);
				t.type = "all";
				t.name = l;
				t.dict["SHELL"] = [];
				if tar.type in kws.CPLOBJ:
					if l == "clean":
						if tar.tpl() == "sub":
							for submk in tar.wzdict("SUBMK"):
								t.dict["SHELL"].append("-make clean -C "+submk);
							t.dict["SHELL"].append("-rm -rf output");
						else:
							t.dict["SHELL"].append("-rm -rf $("+tar.fname() + "_OBJS) $(" + tar.fname() +"_IDLSRCCPP) $(" \
									+ tar.fname() + "_IDLSRCH) " + tar.name + ".range conf/" + tar.name + ".range");
							t.dict["SHELL"].append("-rm -rf "+tar.name);
							t.dict["SHELL"].append("-rm -rf output");
							t.dict["SHELL"].append("-rm -rf ccp_output.error   ccp_output_scm.xml  ccp_output.xml ccp_output.pclint  ccp_output.txt");
					elif l == "output" and tar.type == kws.TARGET:
						t.dict["SHELL"].append("mkdir -p output");
						if tar.tpl() == "app":
							t.dict["SHELL"].append("mkdir -p output/bin");
							t.dict["SHELL"].append("cp -rf " + tar.name + " output/bin");
							t.dict["SHELL"].append("`if [ -e \"conf\" ];then cp -rf conf output/ ;fi`\n");
						elif tar.tpl() == "sub":
							for submk in tar.wzdict("SUBMK"):
								t.dict["SHELL"].append("-make output -C "+submk);
								t.dict["SHELL"].append("`if [ -d \""+submk+"/output\" ];then cp -rf "+submk+"/output/*	output/ ;fi`\n");
						else:
							t.dict["SHELL"].append("-mkdir -p output/lib");
							t.dict["SHELL"].append("-cp -rf " + tar.name + " output/lib");
							t.dict["SHELL"].append("-mkdir -p output/include");
							t.dict["SHELL"].append("-cp -rf $("+tar.fname()+"_HEADERS) output/include");
							t.dict["SHELL"].append("`if [ -e \"conf\" ];then cp -rf conf output/ ;fi`\n");
					elif l == "ccpc":
						if tar.tpl() == "sub":
							for submk in tar.wzdict("SUBMK"):
								t.dict["SHELL"].append("-make ccpc -C " + submk);
						else:
							t.dict["SHELL"].append("ccp $("+tar.fname()+"_SOURCES) --formatter vim");
				else: 
					if l == "cov" :
						t.dict["SHELL"].append("cov01 -1");
						t.dict["SHELL"].append("make clean");
						t.dict["SHELL"].append("make " + tar.name);
						t.dict["SHELL"].append("cov01 -0");
					else:
						for x in tar.tarlst:
							if x.type in kws.CPLOBJ:
								t.dict["SHELL"].append("$("+x.fname()+"_"+l+")");
				tar.tarlst.append(t);


	def cc_tar(self, tar, level):
		if level > 2:
			return "";
		if not tar.type:
			if kws.IDLNODIR in tar.wzdict(kws.CONFIG):
				fn = os.path.dirname(os.path.realpath(__file__)) + "/nodir_make.tpl";
			else:
				fn = os.path.dirname(os.path.realpath(__file__)) + "/make.tpl";
		elif tar.type in kws.CPLOBJ:
			if kws.IDLNODIR in tar.wzdict(kws.CONFIG):
				fn = os.path.dirname(os.path.realpath(__file__)) + "/nodir_tar_app.tpl";
			else:
				fn = os.path.dirname(os.path.realpath(__file__)) + "/tar_app.tpl";
		elif tar.type == "all":
			if tar.parent and tar.parent.type == "" and tar.name not in ["output", "clean"]:
				fn = os.path.dirname(os.path.realpath(__file__)) + "/root.tpl";
			else:
				fn = os.path.dirname(os.path.realpath(__file__)) + "/empty.tpl";
		elif tar.type == "src":
			if tar.name[tar.name.rfind(".")+1:] == "c":
				fn = os.path.dirname(os.path.realpath(__file__)) + "/objc.tpl";
			else:
				fn = os.path.dirname(os.path.realpath(__file__)) + "/obj.tpl";
		else:
			return "";

		if "MAKETPL" in tar.dict:
			fn = tar.dict["MAKETPL"][0];

		fp = open (fn);
		maketpl = fp.read();
		fp.close();

		if not tar.type:
			if kws.MAKDEP in tar.wzdict(kws.CONFIG):
				maketpl = maketpl.replace("__$OPEN_MAKDEP_VALUE$__", "-include $(MAKDEP)");
			else:
				maketpl = maketpl.replace("__$OPEN_MAKDEP_VALUE$__", "");

		#加入默认的处理逻辑
		self.add_default_tar(tar);

		scopesp = "";
		if tar.parent:
			scopesp = tar.parent.fname();
		maketpl = maketpl.replace("__$NAME$__", tar.name).replace("__$TYPE$__", tar.type).replace("__$SCOPE$__", scopesp).replace("__$FNAME$__", tar.fname());

		rp = tar;
		while rp:
			for x in rp.dict:
				if x in ["INCPATH", "DEP_INCPATH"]:
					maketpl = maketpl.replace("__$"+x+"_VALUE$__", self.pjoin(" -I", rp.dict[x])).replace("__$"+x+"$__", x);
				elif x in ["LDFLAGS", "DEP_LDFLAGS"]:
					maketpl = maketpl.replace("__$"+x+"_VALUE$__", self.pjoin(" -L", rp.dict[x])).replace("__$"+x+"$__", x);
				else:
					maketpl = maketpl.replace("__$"+x+"_VALUE$__", " ".join(rp.dict[x])).replace("__$"+x+"$__", x);
				maketpl = maketpl.replace("__$"+x+"_LINES$__", "\t"+"\n\t".join(rp.dict[x]));
			rp = rp.parent;

		lnkcmd = "\t@echo \"force_clean\"\n";
		lnkcmdcc = "$(if ifeq($(suffix $(n)), .c), ";
		lnkcmdcc += "$(CC) -c -o $(basename $(n)).o $(n) $(CXXFLAGS) $(CPPFLAGS) $(INCPATH); "
		lnkcmdcc += " , ";
		lnkcmdcc += "$(CXX) -c -o $(basename $(n)).o $(n) $(CXXFLAGS) $(CPPFLAGS) $(INCPATH); "
		lnkcmdcc += ")";
		if "ALL" in tar.wzdict("FORCE_CLEAN"):
			lnkcmd += "\t$(foreach n, $("+tar.fname()+"_SOURCES), "+lnkcmdcc+")\n";
		else:
			lnkcmd += "\t$(foreach n, $(wildcard " + " ".join(tar.wzdict("FORCE_CLEAN")) + "), "+lnkcmdcc+")\n";
		if not tar.wzdict("LINKCMD") and tar.type in kws.CPLOBJ:
			if tar.tpl() == "app":
				lnkcmd += "\t@`for x in $("+tar.fname()+"_CONFDES);do " \
						+ "cpp -C -o "+tar.fname()+".range $$x $(CPPFLAGS) $(INCPATH);"\
						+ "mkdir -p conf;cp "+tar.fname()+".range conf/; done`\n";
				lnkcmd += "\t$(LINK) $^ -o $@ -Xlinker \"-(\" $(LDFLAGS) $(LDLIBS) $(LINKFLAGS) -Xlinker \"-)\"\n";
			elif tar.tpl() == "lib":
				lnkcmd = "\trm -f $@ || echo \n";
				lnkcmd += "\tar cr $@ $^\n";
			elif tar.tpl() == "so":
				lnkcmd = "\trm -f $@ || echo \n";
				lnkcmd += "\t$(LINK) -shared -o $@ $^ -Xlinker \"-(\" $(LDFLAGS) $(LDLIBS) $(LINKFLAGS) -Xlinker \"-)\"\n";
			elif tar.tpl() == "sub":
				#lnkcmd = "\t@echo \"making\"\n";
				#print comake_bin;
				for submk in tar.wzdict("SUBMK"):
					if kws.CHECKOUT:
						os.system("cd "+submk+";"+comake_bin+" --checkout");
					else:
						os.system("cd "+submk+";"+comake_bin);
					lnkcmd += "\tmake -C " + submk + " \n";
					#lnkcmd += "\t`if [ -d \""+submk+"/output\" ];then cp -rf "+submk+"/output/*	output/ ;fi`\n"
		else:
			lnkcmd = "\t"+"\t\n".join(tar.wzdict("LINKCMD"));
		maketpl = maketpl.replace("__$LINKCMD_LINES$__", lnkcmd);

		tar_maketpl = "";
		src_maketpl = "";
		tar_val = "";
		tst_val = "";
		subtar_val = "";
		tar_cmd = "";
		for t in tar.tarlst:
			if t.type == "src":
				src_maketpl += self.cc_tar(t, level+1);
				src_maketpl = src_maketpl.replace("__$NAME_OBJ$__", t.name[:t.name.rfind(".")] + ".o");
			else:
				tar_maketpl += self.cc_tar(t, level+1);
				if t.type == kws.TARGET:
					tar_val += t.name + " ";
					subtar_val += t.name + " ";
					tar_cmd += "\tmake "+t.name+"\n";
					#tar_cmd += "\trm -rf $("+t.name+"_OBJS)\n";
					if tar.wzdict("FORCE_CLEAN"):
						if "ALL" in tar.wzdict("FORCE_CLEAN"):
							tar_cmd += "\t-rm -rf $("+t.name+"_OBJS)\n";
						else:
							tar_cmd += "\t-rm -rf $(addsuffix .o, $(basename "+ "\t".join(tar.wzdict("FORCE_CLEAN")) + "))\n";
				elif t.type == kws.TEST:
					tst_val += "\t./"+t.name + "\n";
					subtar_val += t.name + " ";

		#maketpl = maketpl.replace("__$target_CMDLINE$__", tar_cmd);
		maketpl = maketpl.replace("__$target_VALUE$__", tar_val);
		maketpl = maketpl.replace("__$test_VALUE$__", tst_val.replace("\n", "\t"));
		maketpl = maketpl.replace("__$SUB_ALL_TARGETS$__", subtar_val);
		#maketpl = maketpl.replace("__$RUNALLTEST$__", "\t`for x in "+tst_val+" ;do ./$$x;done`");
		#maketpl = maketpl.replace("__$RUNALLTEST$__", tst_val);
		maketpl = maketpl.replace("__$RUNALLTEST$__", "");
		maketpl = maketpl.replace("__$LIST_ALL_TARGET$__", tar_maketpl);
		maketpl = maketpl.replace("__$SOURCES_RULES$__", src_maketpl);

		return maketpl+"\n";


if __name__ == "__main__":
	p = cokparser.cokparser();
	p.cc(makenv);
	fp = open("test.prj", "r");
	p.cc(fp.read());
	#print p.root;
	q = cokmake();
	print q.cc(p.root);

