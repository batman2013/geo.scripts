# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 18:00:54 2013

@author: songkai
"""

class transnode:
	def __init__(self):
		self.s = ''
		self.t = {} #{'t':score}
		self.n = 0
		self.bestt = ''
		self.kbestt = []
	def find_bestt(self):
		self.bestt = ''
		tmpt = ''
		tmpscore = -1000
		for key in self.t:
			if self.t[key] > tmpscore:
				tmpscore = self.t[key]
				tmpt = key
		self.bestt = tmpt

	def find_kbestt(self, k):
		for i in range(len(self.kbestt)):
			del self.kbestt[0]
		assert len(self.kbestt) == 0
		if k > n or k == n:
			for key in self.t:
				self.kbestt.append(key)
		else:
			pass
def read_phrase(path):
	for line in open(path):
		line = line.decode('utf-8').strip()
		items = line.split(' ||| ')

