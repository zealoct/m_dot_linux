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

class guess:
	pass
	_headers = "headers";
	_libs = "libs";
	_dicth = {};
	_dictl = {};
	def __init__(self):
		base = os.path.dirname(os.path.realpath(__file__));
		if base:
			self._headers = base + "/headers";
			self._libs = base + "/libs";

		fp = open (self._headers, "r");
		lines = fp.readlines();
		fp.close();
		for l in lines:
			x = l.strip();
			bn = os.path.basename(x);
			if bn in self._dicth:
				self._dicth[bn].add(os.path.dirname(x));
			else:
				self._dicth[bn] = set();
				self._dicth[bn].add(os.path.dirname(x));
		fp = open (self._libs, "r");
		lines = fp.readlines();
		fp.close();
		for l in lines:
			x = l.strip();
			bn = os.path.dirname(x);
			if bn in self._dictl:
				self._dictl[bn].add(os.path.basename(x));
			else:
				self._dictl[bn] = set();
				self._dictl[bn].add(os.path.basename(x));

	def guess(self, hd, vmap, vmaph):
		if hd in self._dicth:
			if hd in vmaph:
				vmaph[hd] |= self._dicth[hd];
			else:
				vmaph[hd] = set();
				vmaph[hd] |= self._dicth[hd];

			for x in self._dicth[hd]:
				bn = x;
				bn2 = os.path.dirname(bn);
				bn3 = bn2 + "/lib";
				if bn in self._dictl:
					vmap[bn] = self._dictl[bn];
				if bn2 in self._dictl:
					vmap[bn2] = self._dictl[bn2];
				if bn3 in self._dictl:
					vmap[bn3] = self._dictl[bn3];

	def merge(self, vmaph):
		vset = set();
		for x in vmaph:
			vset |= (vmaph[x]);
		return vset;

if __name__  == "__main__":
	vmap = {};
	vmaph = {};
	guess().guess("ul_log.h", vmap, vmaph);
	guess().guess("nshead.h", vmap, vmaph);
	guess().guess("ul_net.h", vmap, vmaph);
	guess().guess("comdb.h", vmap, vmaph);
	guess().guess("fileblock.h", vmap, vmaph);
	print vmap;
	print vmaph;
	print guess().merge(vmaph);
