#!/usr/bin/python
import re
import commands
import sys
import os
import string
import time

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/libcomake/");
import kws
import cokut

class genprj :
	pass
	_outfile = "";
	_tgfile = "";
	_testmod = ["test", "unittest"];

	def set_outfile(self, outfile):
		self._outfile = outfile;
	def set_target(self, tg):
		self._tgfile = tg;

	def getsources (self):
		src = "";
		for x in cokut.xfindf(".", "*.cpp"):
			if x.find("test") == -1:
				src += "\\\n\t" + x;
		for x in cokut.xfindf(".", "*.c"):
			if x.find("test") == -1:
				src += "\\\n\t" + x;
		return "SOURCES += " + src + "\n";

	def gettestsrc (self):
		src = [];
		for x in cokut.xfindf(".", "*.cpp"):
			if x.find("test") >= 0:
				src.append(x);
		for x in cokut.xfindf(".", "*.c"):
			if x.find("test") >= 0:
				src.append(x);
		return src;

	def getidls (self):
		src = "";
		for x in cokut.xfindf(".", "*.idl"):
			src += "\\\n\t" + x;
		if src:
			return kws.IDLSRC + " = " + src + "\n";
		return "";

	def getmkfn(self, tpl):
		if tpl != "sub":
			return "";
		src = "";
		for x in cokut.xfindf(".", "[Mm]akefile"):
			if x.find("/") != -1 and x.find("test") == -1:
				src += "\\\n\t" + x[:x.rfind("/")];
		if src:
			src = kws.SUBMK + " = " + src + "\n";
		for x in cokut.xfindf(".", "[Mm]akefile"):
			if x.find("/") != -1 and x.find("test") != -1:
				src += "#" + kws.SUBMK + "+=" + x[:x.rfind("/")] + "\n";
		return src;

	def gettgtn (self, tpl):
		if self._tgfile:
			tgtn = self._tgfile;
		else:
			tgtn = os.path.basename(os.getcwd());
		#if tpl == "lib":
		#	tgtn = "lib"+tgtn+".a";
		return tgtn;

	def replace(self, tpl):
		rpldict = { "__$COMAKE_VERSION_VALUE$__":"1.0.1",
				"__$WORKROOT$__":kws.WORKROOT,
				"__$WORKROOT_VALUE$__":cokut.get_workroot(),
				"__$INCPATH$__":kws.INCPATH,
				"__$INCPATH_VALUE$__":".",
				"__$CONFIG$__" : kws.CONFIG,
				"__$CONFIG_VALUE$__" : "MAKDEP",
				"__$SOURCES_LINES$__" : self.getsources(),
				"__$IDLSRC_LINES$__" : self.getidls(),
				"__$TARGET_NAME$__" : self.gettgtn(tpl),
				"__$MODULENAME$__" : "MODULENAME",
				"__$MODULENAME_VALUE$__" : self.gettgtn(tpl),
				"__$TEMPLATE$__" : kws.TEMPLATE,
				"__$TPL$__" : tpl,
				"__$MAKFILE_LINES$__" : self.getmkfn(tpl),
				"__$TIME$__" : time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
				};

		tplf = "/app.prj";
		if tpl == "sub":
			tplf = "/sub.prj";

		fp = open (os.path.dirname(os.path.realpath(__file__)) + tplf);
		text = fp.read();
		fp.close ();

		for x in rpldict:
			text=text.replace(x, rpldict[x]);

		text += "\n";
		#if tpl != "sub":
		#	test = self.gettestsrc();
		#	for x in test:
		#		file = x;
		#		x = x[:x.rfind(".")].replace("/", "_").replace(".","_");
		#		text += "test("+x+"){\n";
		#		text += "SOURCES+="+file+"\n"
		#		text += "}\n";

		return text;

	def prjfile(self, tpl) :
		fp = open (self._outfile, "w");
		fp.write (self.replace(tpl));
		fp.close();

	def run(self, tpl):		
		#cmd = "mkdir -p src conf;"
		#os.system(cmd);
		readme = "README";
		#if not os.path.exists (readme):
		#	os.system("touch " + readme);
		#changelog = "ChangeLog";
		#if not os.path.exists (changelog):
		#	os.system("touch " + changelog);
		if not os.path.exists (self._outfile):
			os.system ("touch " + self._outfile);
		else:
			os.system ("cp -rf " + self._outfile + " ." + self._outfile + ".bk");
		self.prjfile(tpl);

