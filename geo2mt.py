# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 18:00:54 2013

@author: songkai
"""

from read_blk import *

class transnode:
	def __init__(self):
		self.s = ''
		self.t = {} #{'t':score}
		self.n = 0 # number of span that self.s contain from source sentence
		self.ntrans = 0 #number of trans items in self.t
		self.bestt = ''
		self.tag = 'NP'
		self.kbestt = []
		self.beg = None
		self.end = None
		self.indexs = ''
		self.thresoldtrans = []
	def find_bestt(self):
		self.bestt = ''
		tmpt = ''
		tmpscore = -1000
		for key in self.t:
			if self.t[key] > tmpscore:
				tmpscore = self.t[key]
				tmpt = key
		self.bestt = tmpt
	def get_best(self, dic):
		assert len(self.t) > 0
		tmps = -1000
		tmpk = ''
		for key in dic:
			if dic[key] > tmps:
				tmps = dic[key]
				tmpk = key
		return tmpk
	def find_kbestt(self, k):
		assert len(self.t) > 0
		for i in range(len(self.kbestt)):
			del self.kbestt[0]
		assert len(self.kbestt) == 0
		if k > self.ntrans or k == self.ntrans:
			for key in self.t:
				self.kbestt.append(key)
		else:
			tmpdic = self.t
			for i in range(k):
				tmpk = self.get_best(tmpdic)
				self.kbestt.append(tmpk)
				del(tmpdic[tmpk])
	def get_threshold(self, score, islog):
		import math
		if islog == 'islog':
			for key in self.t:
				if math.pow(math.e,self.t[key]) >= score:
					self.thresoldtrans.append(key)
		elif islog == 'notlog':
			for key in self.t:
				if self.t[key] >= score:
					self.thresoldtrans.append(key)
	def set_indexs(self):
		assert self.beg < self.end
		s = ''
		s += '['
		for i in range (self.beg, self.end):
			s += str(i)
			if i != self.end - 1:
				s += ','
		s += ']'
		self.indexs = s

class treenode:
	def __init__(self, _word, _tag, _depid, _dep):
		self.word = _word
		self.tag = _tag
		self.depid = _depid
		self.dep = _dep

def read_phrase(path, transdirec):
	transdic = {}
	for line in open(path):
		line = line.decode('utf-8').strip()
		if len(line) == 0:
			continue
		items = line.split(' ||| ')
		if items[0] == '<NULL>' or items[1] == '<NULL>':
			continue
		if transdirec == 'c2e':
			items[0] = items[0].replace(' ','')
			if not transdic.has_key(items[0]):
				transdic[items[0]] = {}
			if not transdic[items[0]].has_key(items[1]):
				sc = float(items[2].split(' ')[0])
				transdic[items[0]][items[1]] = sc
		elif transdirec=='e2c':
			items[0] = items[0].strip()
			if not transdic.has_key(items[0]):
				transdic[items[0]] = {}
			if not transdic[items[0]].has_key(items[1].strip()):
				sc = float(items[2].split(' ')[0])
				transdic[items[0]][items[1].strip()] = sc
	return transdic

def read_dep_tree(path):
	sens = []
	sens.append([])
	i = 0
	for line in open(path):
		line =line.decode('utf-8').strip()
		if len(line) == 0:
			sens.append([])
			i += 1
		else:
			items = line.split('\t')
			nd = treenode(items[0], items[1], items[2], items[3])
			sens[i].append(nd)
	j = len(sens)-1
	k = 0
	while (not len(sens[j])) and j >= 0:
		del sens[j]
		j -= 1
	while (not len(sens[k])) and k <= len(sens)-1:
		del sens[k]
		k += 1
	return sens

def read_loc_dic(path, transdic):
	for line in open(path):
		line = line.decode('utf-8').strip()
		if len(line) == 0:
			continue
		items = line.split('\t')
		sl = items[0]
		tl = items[1]
		lscore = 0
		if not transdic.has_key(sl):
			transdic[sl] = {}
		if not transdic[sl].has_key(tl):
			transdic[sl][tl] = 0
		transdic[sl][tl] = 0
	return transdic

def get_sp_tp(tree, beg, end, transdic, transdirec):
	sp = ''
	tp = {}
	if transdirec == 'c2e':
		for i in range(beg, end):
			sp += tree[i].word
		if transdic.has_key(sp):
			tp = transdic[sp]
		else:
			return False
	elif transdirec == 'e2c':
		for i in range(beg, end):
			sp += tree[i].word
			if i != end -1:
				sp += ' '
		if transdic.has_key(sp):
			tp = transdic[sp]
		else:
			return False
	return (sp,tp)

def make_sen_input(tree, transdic, max_phrase_size, kbest, islog, transdirec):
	transnodes = []
	for i in range(len(tree)):
		k = len(tree)
		if (max_phrase_size + i) <= len(tree):
			k = max_phrase_size + i
		for j in range(i,k):
			tnode = transnode()
			tnode.beg = i
			tnode.end = j + 1
			if tnode.end == tnode.beg + 1:
				tnode.tag = tree[i].tag
			sp_tp = get_sp_tp(tree, tnode.beg , tnode.end ,transdic, transdirec)
			if not sp_tp:
				continue
			tnode.s = sp_tp[0]
			tnode.t = sp_tp[1]
			tnode.ntrans = len(tnode.t)
			tnode.n = tnode.end - tnode.beg
			tnode.find_bestt()
			if kbest > 1:#is a number of kbest trans
				tnode.find_kbestt(kbest)
			elif kbest < 1:#is a thresold of trans score
				tnode.get_threshold(kbest, islog)
				if len(tnode.thresoldtrans) == 0:
					continue
			tnode.set_indexs()
			transnodes.append(tnode)
	return transnodes
def get_logs(chtree, entree):
	chs = ''
	ens = ''
	for node in chtree:
		chs += node.word
		chs += ' '
	for node in entree:
		ens += node.word
		ens += ' '
	return (chs,ens)
def make_allsen(trees, entrees, transdic, max_phrase_size, kbest, islog, transdirec):
	allsens = []
	logs = []
	treeindex = 0
	for tree in trees:
		allsens.append([])
		logs.append([])
		transnodes = make_sen_input(tree, transdic, max_phrase_size, kbest, islog, transdirec)
		for tnode in transnodes:
			ss = ''
			if kbest < 1: #it's a thresold
				c = 0
				for tran in tnode.thresoldtrans:
					if tran.find(' ') != -1:
						tran = tran.replace(' ','_')
						tran = '__' + tran
						tran += '__'
					ss += tran
					if c != len(tnode.thresoldtrans)-1:
						ss += ' '
					c += 1
			elif kbest == 1:
				if tnode.bestt.find(' ') != -1:
					ss = '__' + tnode.bestt.replace(' ','_') + '__'
				else:
					ss = tnode.bestt
			else:
				c = 0
				for tran in tnode.kbestt:
					if tran.find(' ') != -1:
						tran = tran.replace(' ','_')
						tran = '__' + tran
						tran += '__'
					ss += tran
					if c != len(tnode.kbestt)-1:
						ss += ' '
					c += 1
			allsens[treeindex].append(tnode.indexs + '\t' + tnode.tag + '\t' + ss)
			logs[treeindex].append(tnode.indexs + '\t' + tnode.tag + '\t' + ss)
		logs[treeindex].append(get_logs(tree, entrees[treeindex])[0])
		logs[treeindex].append(get_logs(tree, entrees[treeindex])[1])
		treeindex += 1
	return (allsens, logs)

def print_reference(path, r_tree):
	out = open(path, 'w')
	for tree in r_tree:
		for node in tree:
			depl = node.dep
			if node.dep != 'ROOT':
				depl = 'N'
			out.write((node.word + '\t' + node.tag + '\t' + node.depid +'\t' +depl).encode('utf-8') + '\n')
		out.write('\n')
	out.close()

def printout(allsens, chtrees, path):
	out = open(path, 'w')
	c = 0
	for tree in allsens:
		for transitem in tree:
			out.write(transitem.encode('utf-8') + '\n')
		out.write('\n')
		i = 0
		for node in chtrees[c]:
			out.write(str(i) + '\t' + node.depid + '\t' + node.dep + '\n')
			i += 1
		out.write('\n')
		c += 1

if __name__=='__main__':
	import sys
	chtrees = read_dep_tree(sys.argv[1]) #src tree
	entrees = read_dep_tree(sys.argv[2]) #tgt tree
	transdic = read_phrase(sys.argv[3], sys.argv[8]) #phrase table; transdirec
	transdic = read_loc_dic(sys.argv[4], transdic) #loc dic
	(allsens, logs) = make_allsen(chtrees, entrees, transdic, int(sys.argv[5]), float(sys.argv[6]), sys.argv[7], sys.argv[8]) # max phrase size; kbest; is a log socre; trans direction
	printout(allsens, chtrees, sys.argv[9]) #mt file path
	printout(logs, chtrees, sys.argv[9]+'.log') #mt log file path
	#print_reference(sys.argv[1],entrees)
