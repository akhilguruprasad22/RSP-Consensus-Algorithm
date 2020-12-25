from flask import Flask,request,render_template,redirect,url_for
from core import blockchain
from argparse import ArgumentParser
import requests
import time
import json

currentPort=0
uCombs={}
winners={}
winner=0
rcomb={}
app = Flask(__name__)
bc = blockchain()

@app.route('/chain',methods=['GET'])
def displayChain():
	return bc.displayChain()

@app.route('/peers/get',methods=['GET'])
def getPeers():
	return {
	'peers': bc.user.peers
	}

@app.route('/postComb',methods=["POST"])
def combinations():
	global uCombs

	data = request.get_json(force=True)
	uCombs.update(data)
	return 'Combinations have been updated.'

@app.route('/getRSPcomb',methods=["POST"])
def getRSPcomb():
	global rcomb
	data = request.get_json(force=True)
	rcomb = data["RSPcomb"]
	return 'Common RSP combination received'

@app.route('/winner',methods=["POST"])
def decideWinner():
	global winners
	global winner
	maxwins=0
	data = request.get_json(force=True)
	dk = list(data.keys())

	if dk[0] in winners.keys():
		winners[dk[0]]+=1
	else:
		winners[dk[0]]=1
	
	for key,value in winners.items():
		if winners[key]>maxwins:
			winner=key
	return 'Winner decided'	

@app.route('/mine/addBlock',methods=["POST"])
def addblk():
	data = request.get_json(force=True)
	bc.addBlock(data["data"])
	return 'Block added.'

@app.route('/mine',methods=['POST'])
def mine():
	global uCombs
	global rcomb
	global winner

	coin = bc.user.calcCoin('i7',16)
	comb = bc.user.genComb(coin)
	uCombs[str(currentPort)]=comb

	Sum=0
	N = len(bc.user.peers)

	for peer in bc.user.peers:
		if peer!=currentPort: 
			r=requests.post('http://127.0.0.1:{}/postComb'.format(peer),json={str(currentPort):comb})
			print(r.text)
	time.sleep(5)
	
	for i in uCombs.keys():
		if uCombs[i][0]=='S':
			Sum+=1
		elif uCombs[i][0]=='P':
			Sum+=2

	delegator = Sum%N

	print("delegator:",delegator)

	if bc.user.peers[delegator]==currentPort:
		print(uCombs)
		rcomb = bc.user.genComb(len(max(uCombs,key=len)))
		
		for peer in bc.user.peers:
			if peer!=currentPort:
				r=requests.post('http://127.0.0.1:{}/getRSPcomb'.format(peer),json={"RSPcomb":rcomb})
				print(r.text)
	else:
		time.sleep(5)
		wins={}
		for port in uCombs.keys():
			wins[port]=bc.RSP(rcomb,comb)
			if wins[port] > winner:
				winner=port

		for peer in bc.user.peers:
			if peer!=currentPort:	
				r=requests.post('http://127.0.0.1:{}/winner'.format(peer),json={str(winner):1})
				print(r.text)
		time.sleep(5)

	blockdata = request.get_json()
	bc.addBlock(blockdata["data"])

	for peer in bc.user.peers:
		if peer!=currentPort:	
			r=requests.post('http://127.0.0.1:{}/mine/addBlock'.format(peer),json=blockdata)
			print(r.text)
	
	uCombs={}
	winners={}
	rcomb={}

	if int(winner)==currentPort:
		print('You are the winner. Block Added.')
	winner=0
	
	return 'Consensus complete.'

@app.route('/validitycheck',methods=["GET"])
def validityCheck():
	if blockchain.isValid(bc.chain):
		return 'Chain is Valid.'
	else:
		return 'Chain is Invalid'

if __name__ == '__main__':
	parser = ArgumentParser(description='Blockchain Command Line')
	parser.add_argument(
		'-ho',
		'--host',
		default='127.0.0.1',
		help='host to run service')
	parser.add_argument(
		'-p',
		'--port',
		default=5000,
		type=int,
		help='port to run service')
	parser.add_argument(
		'-n',
		'--neighbors',
		nargs='+',
		required=True,
		type=int,
		help='neighboring ports <Required>')

	args=parser.parse_args()	
	for i in args.neighbors:
		if bc.user.addPeer(i):
			print("Peer added.")
		else:
			print("Invalid peer. Will not be added.")
	bc.user.addPeer(args.port)
	
	currentPort=args.port
	print("currentPort:",currentPort)

	app.run(host=args.host,port=args.port,debug=True)