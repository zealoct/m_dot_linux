#!/usr/bin/python

import re
import commands
import sys
import os
import string
import time

sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/libcomake/");
import kws
import cokut
import cokgen
#import cokmk
import cokmake

class genstand :
	pass
	_outfile = "";
	_mkdir = False;

	def set_outfile(self, outf):
		self._outfile = outf;

	def set_mkdir(self, boolen):
		self._mkdir = boolen;

	def gendirs(self):
		if self._mkdir == True:
			os.system("mkdir -p "+self._outfile);
			os.chdir(self._outfile);

		#cmd = "mkdir -p " + kws.DIRSRC + " " + kws.DIRTEST + " " + kws.DIRCONF;
		cmd = "mkdir -p " + kws.DIRSRC + " " + kws.DIRCONF;
		os.system(cmd);
		if not os.path.exists(kws.FILEREADME):
			os.system("touch " + kws.FILEREADME);
		if not os.path.exists(kws.FILECHANGELOG):
			os.system("touch " + kws.FILECHANGELOG);
	def run (self, flag, gprj, gmk):
		self.gendirs();

		os.chdir (kws.DIRSRC);
		if not os.path.exists("main.cpp"):
			if flag == "app":
				os.system("echo \"int main ()\" > main.cpp");
				os.system("echo \"{\" >> main.cpp");
				os.system("echo \"     return 0;\" >> main.cpp");
				os.system("echo \"}\" >> main.cpp");
			elif flag == "lib":
				os.system("touch main.cpp");
		gprj.set_outfile(kws.DIRSRC + ".prj");
		gprj.set_target(self._outfile);
		gprj.run (flag);
		gmk.set_prjfile(kws.DIRSRC+".prj");
		gmk.set_outfile("Makefile");
		gmk.run();

		'''
		os.chdir ("../");
		os.chdir (kws.DIRTEST);
		if not os.path.exists("main.cpp"):
			os.system("echo \"int main ()\" > main.cpp");
			os.system("echo \"{\" >> main.cpp");
			os.system("echo \"     return 0;\" >> main.cpp");
			os.system("echo \"}\" >> main.cpp");

		gprj.set_outfile(kws.DIRTEST+".prj");
		gprj.set_target(kws.DIRTEST);
		gprj.run ("app");
		gmk.set_prjfile(kws.DIRTEST+".prj");
		gmk.set_outfile("Makefile");
		gmk.run();
		''';

		os.chdir("../");
		gprj.set_outfile(self._outfile+".prj");
		gprj.run("sub");
		gmk.set_prjfile(self._outfile+".prj");
		gmk.set_outfile("Makefile");
		gmk.run();

