#!/usr/bin/env python
#coding:gbk
import re
import commands
import sys
import os
import string
import time

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/libcomake/");
import kws

#text = expr | scope 
#expr = word asg value
#word = \w+
#asg = [+|-|?]=
#value = [^\n]+
#scope = scope_header scope_tail?
#scope_header = word (word)? {text}
#scope_tail = else {text} | else scope

#keywords:
#linux32:	32平台
#linux64:	64平台
#debug:		debug版本
#if	:	条件判断
#else	:	

class parser_exp(BaseException):
	pass

class text_exp(parser_exp):
	pass

class expr_exp(parser_exp):
	pass

class scope_exp(parser_exp):
	pass

class word_exp(parser_exp):
	pass

class asg_exp(parser_exp):
	pass

class value_exp(parser_exp):
	pass

class scope_header_exp(parser_exp):
	pass

class scope_tail_exp(parser_exp):
	pass

class token_word_exp(parser_exp):
	pass

class tarobj_split_exp(parser_exp):
	pass

class tarobj:
	pass
	wordunit = "((\"(\\.|[^\"])*\")+|[^\"\s]+)";
	replag = "asdf!@#$%^&*defad+_)(*asdfePOIIY";
	def __init__(self, parent):
		self.dict = {};
		self.tarlst = [];
		self.parent = parent;
		self.type = "";
		self.name = "";
		self.tplt = "";

	def judgetpl(self):
		if "TARNAME" in self.dict:
			self.name = "".join(self.dict["TARNAME"]);
		if self.type != "target":
			return ;
		tplt = " ".join(self.wzdict("TEMPLATE")).strip();
		if tplt in ["app", "so", "sub", "lib", "no"]:
			self.tplt = tplt;
		if tplt in ["so", "lib"]:
			if self.name[:3] != "lib":
				if tplt == "so":
					self.name = "lib" + self.name + "." + tplt;
				else:
					self.name = "lib" + self.name + ".a";
	
	def allval(self, key):
		lst = [];
		if key in self.dict:
			for l in self.dict[key]:
				lst.append(l);
		for t in self.tarlst:
			for l in t.allval(key):
				lst.append(l);

		return lst;

	def fname(self):
		return self.name.replace(".", "_");

	def tpl(self):
		if self.tpl == "no":
			return "no";
		if len(self.name) > 5:
			if self.name[:3] == "lib" and self.name[-2:] == ".a":
				return "lib";
		if len(self.name) > 6:
			if self.name[:3] == "lib" and self.name[-3:] == ".so":
				return "so";
		if self.tplt:
			return self.tplt;
		return "app";

	def wzdict(self, key):
		if key in self.dict:
			return self.dict[key];
		elif self.parent:
			return self.parent.wzdict(key);
		return [];

	def assign(self, key, val):
		self.dict[key] = self.parser(key,val);

	def envasg(self, key, val):
		if key in os.environ:
			self.assign(key, os.environ[key]);
		else:
			self.assign(key, val);

	def starasg(self, key, val):
		lst = [];
		for x in self.wzdict(key):
			lst.append(x);
		self.dict[key] = lst;
		for x in self.parser(key, val):
			if x not in self.dict[key]:
				self.dict[key].append(x);

	def append(self, key, val):
		lst = [];
		for x in self.wzdict(key):
			lst.append(x);
		self.dict[key] = lst;
		for x in self.parser(key,val):
			self.dict[key].append(x);


	def remove(self, key, val):
		lst = [];
		for x in self.wzdict(key):
			lst.append(x);
		self.dict[key] = lst;
		for x in self.parser(key,val):
			if x in self.dict[key]:
				self.dict[key].remove(x);

	def split(self, val):
		pos = 0;
		start = 0;
		skip = 0;
		lst = [];
		while pos < len(val):
			if val[pos] == "\\":
				pos += 1;
			elif val[pos] == "\"":
				if skip == 0:
					skip = 1;
				else:
					skip = 0;
			elif val[pos] in [" ", "\t", "\r", "\n", "\f"]:
				if skip == 0:
					if val[start:pos].strip():
						lst.append(val[start:pos].strip());
					start = pos + 1;
			pos = pos + 1;
		if pos > start:
			lst.append(val[start:pos].strip());
		#print lst;
		return lst;

	def parser(self, key, val):
		if not val:
			return [];
		ret = [];
		if key in ["SHELL", "LINKCMD"]:
			ret.append(val);
			return ret;
		for x in self.split(val):
			lst = re.findall("\$\w+", x);
			for y in lst:
				x = x.replace(y, self.wzdict(y[1:]));
			for y in self.split(x):
				ret.append(y);
		return ret;



	def pspace(self, level):
		info = "";
		while level > 0:
			info = info + "\t";
			level -= 1;
		return info;

	def __repr__(self, level=0):
		info = self.pspace(level) + "{\n";
		info += self.pspace(level+1) + "{type:" + self.type + \
				", name:"+ self.name + "}\n";
		info += self.pspace(level+1) + self.dict.__repr__() + "\n";
		for tar in self.tarlst:
			info += tar.__repr__(level+1) ;
		info += self.pspace(level) + "}\n";
		return info;

class cokparser:
	pass

	sp = '[ \t\r\v\f]*';
	wordrgx = '^\s*([a-zA-Z_][\w|\.]*)' + sp;
	asgrgx = '^' + sp + '([+|\-|?|*]?=)' + sp;
	valuergx = '^([^\n]*)';
	maxlevel = 100000000;

	keyword_dict = {
			kws.LINUX32:maxlevel, kws.LINUX64:maxlevel, kws.DEBUGSCOPE:maxlevel, kws.TARGET:1, 'all':maxlevel, 'else':maxlevel, kws.TEST : 1, "src" : 1
	};
	mustexpr_dict = {
			kws.TARGET : 1, 'all' : 1, kws.TEST : 1, 'src' : 1
	}

	def __init__(self):
		self.text = "";
		self.pos = 0;
		self.level = 0;
		self.root = tarobj("");
		self.tar = self.root;
		self.act = 1;
		self.jdict = {kws.LINUX32:0, kws.LINUX64:0, kws.DEBUGSCOPE:0};
		self.env = {
				kws.LINUX32:os.popen("uname -i 2>/dev/null").read().strip() != "x86_64",
				kws.LINUX64:os.popen("uname -i 2>/dev/null").read().strip() == "x86_64",
				kws.DEBUGSCOPE:1==0};

	def pre(self):
		txt = "";
		for x in self.text.replace("\\\n", "").split("\n"):
			if x and x[0] == "#":
				continue;
			txt += x + "\n";
		self.text = txt;

	def cc(self, text, env={}):
		self.text = text;
		self.pos = 0;
		self.level = 0;
		self.act = 1;
		if env:
			self.env = env;
		self.pre();

		self.cc_text();
		if self.token_char():
			raise parser_exp, "find unknow word at line " + self.line();

	def line(self):
		return str(self.text[:self.pos].count("\n")+1);

	def cc_text(self):
		self.level += 1;
		try:
			while 1:
				pos = self.pos;
				if self.token_word() in self.keyword_dict:
					self.cc_scope();
				else:
					self.cc_expr();
				if pos == self.pos:
					break;
		except token_word_exp, e:
			pass
		finally:
			self.level -= 1;

	def cc_expr(self):
		key = self.cc_word();
		asg = self.cc_asg();
		val = self.cc_value();

		if self.act == 1:
			if asg == "=":
				self.tar.assign(key, val);
			elif asg == "+=":
				self.tar.append(key, val);
			elif asg == "-=":
				self.tar.remove(key, val);
			elif asg == "?=":
				self.tar.envasg(key, val);
			elif asg == "*=":
				self.tar.starasg(key, val);

	def cc_word(self):
		m = re.search(self.wordrgx, self.text[self.pos:]);
		if m is None:
			raise word_exp, "can't find word at line " + self.line();
		self.pos += len(m.group());

		return m.group(1);

	def token_word(self):
		pos = self.pos;
		m = re.search(self.wordrgx, self.text[pos:]);
		if m is None:
			raise token_word_exp, "tokenword can't find word at line " + self.line();

		return m.group(1);

	def cc_asg(self):
		m = re.search(self.asgrgx, self.text[self.pos:]);
		if m is None:
			raise asg_exp, "can't find asg at line " + self.line();
		self.pos += len(m.group());

		return m.group(1);

	def cc_value(self):
		m = re.search(self.valuergx, self.text[self.pos:]);
		if m is None:
			raise value_exp, "can't find value";
		self.pos += len(m.group());
		return m.group(1);

	def cc_scope(self):
		act = self.act;
		word = self.cc_scope_header();
		try:
			if self.token_word() == 'else':
				self.cc_scope_tail(word);
		except token_word_exp, e:
			pass
		finally:
			self.act = act;

	def cc_space(self):
		while self.text[self.pos:] and (self.text[self.pos] == ' ' 
				or self.text[self.pos] == '\n'
				or self.text[self.pos] == '\t' 
				or self.text[self.pos] =='\r' 
				or self.text[self.pos] == '\v' 
				or self.text[self.pos] == '\f'):
			self.pos = self.pos + 1;

	def cc_char(self):
		self.cc_space();
		if self.text[self.pos:]:
			self.pos =  self.pos + 1;
			return self.text[self.pos-1];
		return "";

	def token_char(self):
		self.cc_space();
		if self.text[self.pos:]:
			return self.text[self.pos];
		return "";

	def back_char(self):
		self.pos = self.pos - 1;

	def cc_scope_header(self):
		scope = self.cc_word();
		expr = "";
		if self.cc_char() == '(':
			expr = self.cc_word();
			ck = self.cc_char();
			while ck == '-':
				expr += '-' + self.cc_word();
				ck = self.cc_char();
			if ck != ")":
				raise scope_header_exp, "can't match )";
			#kws.debug_log("[key:"+scope+"] value["+expr+"]");
		else:
			self.back_char();

		if scope.strip() in self.mustexpr_dict and not expr:
			raise scope_header_exp, scope + " must has expr (...) " + self.line();

		#判断分支是否有效
		if self.act == 1 and scope.strip() in self.env:
			if self.env[scope.strip()]:
				self.act = 1;
			else:
				self.act = 0;
		if scope.strip() in self.jdict:
			self.jdict[scope.strip()] = 1;

		oldtar = "";
		if scope.strip() in [ kws.TEST, kws.TARGET, "all", "src" ]:
			for x in self.tar.tarlst:
				if x.name == expr.strip():
					raise scope_header_exp, scope + " has same name " \
							+ expr + " at line " + self.line();
			if self.act == 1:
				tar = tarobj(self.tar);
				tar.type = scope.strip();
				tar.name = expr.strip();
				self.tar.tarlst.append(tar);
				oldtar = self.tar;
				self.tar = tar;

		if self.cc_char() != '{':
			raise scope_header_exp, "can't find {";

		self.cc_text();

		if self.cc_char() != '}':
			raise scope_header_exp, self.cc_char() + " can't match } at line " + self.line();

		if self.act == 1 and oldtar:
			self.tar.judgetpl();
			self.tar = oldtar;

		if self.act == 1:
			self.act = 0;
		else:
			self.act = 1;
		return scope.strip();

	def cc_scope_tail(self, word):
		self.cc_word();
		if self.cc_char() == '{':
			self.cc_text();
			if self.cc_char() != '}':
				raise scope_tail_exp, "can't match }";
			self.act = 1;
		else:
			self.back_char();
			self.cc_scope();

if __name__ == "__main__":
	try:
		fp = open(sys.argv[1], "r");
		p = cokparser();
		p.cc(fp.read());
		print p.root
	except BaseException, e:
		print "BASE:EXCEPTION";
		print e;
