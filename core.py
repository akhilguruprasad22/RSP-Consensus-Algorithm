from datetime import datetime
import hashlib
import pandas as pd
import random
from requests import get


class user:
	def __init__(self):
		#self.ip=get('https://api.ipify.org').text
		self.peers=[]
		self.coin=0
		self.choices = ['R','S','P']
		self.combination = ''

	def addPeer(self,port):
		if port in range(1024,65500):
			self.peers.append(port)
			self.peers.sort()
			return True
		return False

	def calcCoin(self,CPU,RAM):
		Rfile=pd.read_csv("ram.csv",index_col=0)
		Cfile=pd.read_csv("cpu.csv",index_col=0)
		self.coin=Rfile.loc[RAM][0]+Cfile.loc[CPU][0]

		return self.coin 
	
	def genComb(self,co):
		for _ in range(co):
			self.combination+=random.choice(self.choices)
		
		return self.combination



class block:
	def __init__(self,timestamp,data,bhash,lastHash):
		self.timestamp=timestamp
		self.data=data
		self.bhash=bhash
		self.lastHash=lastHash

	@staticmethod
	def hashfunc(dataInput):
		return hashlib.sha256(str.encode(dataInput)).hexdigest()

	@classmethod
	def genGenesis(cls):
		return cls('1','gendata',cls.hashfunc('1'+'0000'+'gendata'),'0000')

	@property
	def display(self):
		return {
			"timestamp": self.timestamp,
			"data": self.data,
			"bhash": self.bhash,
			"lastHash": self.lastHash
		}



class blockchain:
	def __init__(self):
		self.chain = [block.genGenesis()]
		self.user=user()

	def addBlock(self,data):

		timestamp = datetime.now()
		lastHash = self.chain[len(self.chain)-1].bhash
		bhash = block.hashfunc(str(timestamp)+lastHash+data)

		nblock = block(timestamp,data,bhash,lastHash)

		self.chain.append(nblock)

	def displayChain(self):
		return { i: self.chain[i].display for i in range(len(self.chain)) }

	def RSP(self,rCom,combination):
		wins=0

		for (i,j) in zip(rCom,combination):
			if i==j:
				wins+=1
		return wins


	@staticmethod
	def isValid(chain):
		test = block.genGenesis()
		if chain[0].bhash!=test.bhash:
			return False

		for i in range(len(chain)-1):
			if chain[i].bhash!=chain[i+1].lastHash:
				return False
			if chain[i].bhash!=block.hashfunc(str(chain[i].timestamp)+chain[i].lastHash+chain[i].data):
				return False
		if chain[-1].bhash!=block.hashfunc(str(chain[-1].timestamp)+chain[-1].lastHash+chain[-1].data):
				return False		
		return True
