import socket
import hashlib
#import flask nono need
import threading
import time
from p2pnetwork import node
import math


global user_id
global globalBlockchain
global canStartMining
global options
global otherIps
global p2pnode
otherIps = []



canStartMining = 0

user_id = 1
globalBlockchain = []
genesisHash = "6e31633822177790dd38702db12495af223e72b684ab5950bc4cde10"

nonce = 0

# not using this because its a webapp now
#debug = int(input("Should debug mode be on? (0 or 1)\n"))
debug = 0
#init sha3_224
s = hashlib.sha3_224()
if(debug == 1):

  print(s.name + " algorithm initialized")

  #sha3_224 digest size
  print("digest size: " + str(s.digest_size))

  #test genesis hash
  s.update(b"Sat, Dec 18, 2021")
  print("test genesis hash: ")
  print(s.hexdigest())
  print("expected hash:")
  print(genesisHash)
  if(s.hexdigest() == genesisHash):
    print("hash is ok! proceeding.")
  else:
    print("hash was incorrect!")
    quit(1)
  
  testTransaction1 = {
    "startUser": "server",
    "endUser": "u2",
    "amount": "10"
  }
  testTransaction2 = {
    "startUser": "u2",
    "endUser": "u1",
    "amount": "20"
  }
  
  nonce = 0
  foundHash = 0
  while foundHash == 0:
    nonce += 1
    testBlock = []
    testBlock.append(nonce)
    testBlock.append(genesisHash)
    testBlock.append(testTransaction1)
    testBlock.append(testTransaction2)
    s.update(bytes(str(testBlock), "utf-8"))
    hash = s.hexdigest()
    if(hash[:5] == "00000"):
      testBlock.append(hash)
      foundHash = 1
  print("testBlock: " + str(testBlock))
  print("nonce for testBlock: " + str(nonce))
  print("hash of testBlock: " + hash)
  print("DEBUG OVER, PROCEEDING TO MAIN APP")
  print("\n")

#actually do stuff
print("Quantonium v0.1")

global t1
global t2
global t3
def blockchainMinerLoop():
  global canStartMining
  global globalBlockchain

  genesisBlock = ["-1", 
  "6e31633822177790dd38702db12495af223e72b684ab5950bc4cde10"]
  blockchain = [genesisBlock]
  globalBlockchain = blockchain
  while True:
    print("blockchain: " + str(globalBlockchain)+"\n")
    nonce = 0
    foundHash = 0
    transaction = {
      "startUser": "server",
      "endUser": user_id,
      "amount": "10"
    }
    prevBlock = blockchain[-1]
    prevHash = prevBlock[-1]
    while foundHash == 0:
      nonce += 1
      block = []
      block.append(nonce)
      block.append(prevHash)
      block.append(transaction)
      s.update(bytes(str(block), "utf-8"))
      hash = s.hexdigest()
      if(hash[:5] == "00000"):
        block.append(hash)
        foundHash = 1
    blockchain.append(block)
    globalBlockchain = blockchain
    #TODO: add p2p connection

t1 = threading.Thread(target=blockchainMinerLoop)

def p2pStart():
  global otherIps
  global p2pnode
  def node_callback(event, node, connected_node, data):
    try:
        if event != 'node_request_to_stop': # node_request_to_stop does not have any connected_node, while it is the main_node that is stopping!
            print('Event: {} from main node {}: connected node {}: {}'.format(event, node.id, connected_node.id, data))

    except Exception as e:
      print(e)

  # The main node that is able to make connections to other nodes
  # and accept connections from other nodes on port 8001.
  p2pnode = node.Node("0.0.0.0", 80, node_callback)

  # Do not forget to start it, it spins off a new thread!
  p2pnode.start()
  time.sleep(1)

  while True:
   for x in range(0, len(otherIps)):
      p2pnode.connect_with_node(otherIps[x], 80)
      p2pnode.send_to_nodes('{"message": "OLPing"}')
      time.sleep(0.05) # connection throttling sucks ass


  # Gracefully stop the node.
  p2pnode.stop()

t3 = threading.Thread(target=p2pStart)

#start flask
#t2.start()
#print("Flask/Browser View thread started.")
t3.start()

time.sleep(1)
def getOptions(): 
  global options
  global t1
  global t3
  global otherIps
  options = input("Would you like to CONFIGURE NODEWEB (1), SEND QTM (2), or MINE QTM (3)?\n\n")

  try:
    options = int(options)
  except:
    print("try again, that isn't a number")
    getOptions()
  if(options == 1):
    print("IP List: " + str(otherIps))
    addip = input("What other IP should we add to your node?\n")
    otherIps.append(socket.gethostbyname(addip))
    getOptions()
  if(options == 3):
    t1.start()

getOptions()
