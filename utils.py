import numpy as np
import bisect
from minorminer import find_embedding



class InitMap:
	def __init__(self, initMap,final_embed, bestCount, improveCount=8):
		self.initMap = initMap
		self.bestCount = bestCount
		self.patience = improveCount
		self.bestEmbed = final_embed
		self.curPatience = self.patience

	def update(self, best, embedding):
		if best < self.bestCount:
			self.bestCount = best
			self.bestEmbed = embedding

	def resetPatience(self):
		self.curPatience = self.patience

def getI(m, t, r):
    return (m -t/2 - ((m-t/2)**2 + 2* (m-r) *t)**0.5)/(t)

class InitEmbeddingPool:
	def __init__(self, size, variance, randomRatio, bonusBias= 1) -> None:
		self.maxSize = size
		self.variance = variance
		self.randomRatio = randomRatio
		self.bonusBias = bonusBias
		self.pool = []

	def size(self):
		return len(self.pool)

	def insert(self, initMap):
		bisect.insort_left(self.pool, initMap, key= lambda map: map.bestCount)
		if len(self.pool) > self.maxSize:
			self.pool.pop()
	def update(self, index, initMap):
		self.pool.pop(index)

		self.insert(initMap)
	
	def getIndex(self, ratio):
		if ratio > 1 - self.randomRatio:
			return -1
		avg = (1-self.randomRatio) / self.size()
		upbound = avg*(1+self.variance)
		lowbound = avg*(1-self.variance)
		interval = (upbound - lowbound) / (self.size() - 1)

		index = int(getI(upbound, interval, ratio))
		return index
	
	def pop(self, index):
		return self.pool.pop(index)

	def getInit(self, index):
		return self.pool[index]
	
	def getBest(self, k=1):
		if k == 1:
			return self.pool[0]
		else:
			return self.pool[:k]
	
	def show(self):
		counts = [a.bestCount for a in self.pool]
		print(counts)
		
	def reducePatience(self, index):
		self.pool[index].curPatience -= 1
		bonus = self.bonusBias * int(self.pool[index].patience * (self.maxSize - index) / self.maxSize)
		if self.pool[index].curPatience + bonus <=0:
			print(f"pop index {index}, curPatience: {self.pool[index].curPatience}, bonus: {bonus}")
			self.pop(index)


def BandWidthMatrix(dim, s):
	w = (s-1)// 2
	M = np.zeros((dim, dim))
	for i in range(dim):
		for j in range(max(0, i-w), min(i+w+1, dim)):
			M[i,j] = 1
	return M

def BiKgraph(k, internal=False):
	res = []
	for i in range(k):
		for j in range(k):
			res.append((i,k+j))
	if internal:
		for i in range(k-1):
			res.append((i,i+1))
			res.append((k+i, k+i+1))
	return res


def pyG2CppG(graph, name):
	vertex = max(max(graph, key= lambda a:max(a)))+1
	a = [str(e[0]) for e in graph]
	b = [str(e[1]) for e in graph]
	res = f"graph::input_graph {name}({vertex}, {'{'+','.join(a)+'}'}, {'{'+','.join(b)+'}'});"
	return res

def getEmbed(embedding, var_num):

	embed = {}
	for k in range(var_num):

		embed[k] = embedding[k]

	init_embed = {k : embedding[k+var_num] for k in range(var_num)}
	return embed, init_embed

def getCount(embedding):
	physical_count = sum([len(embedding[k]) for k in embedding.keys()])
	return physical_count