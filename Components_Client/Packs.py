import json
import time
from random import randint

import sqlite3

import Utils.BlazeFuncs as BlazeFuncs
import Utils.Globals as Globals


def getPacks(self, data_e):
	packet = BlazeFuncs.BlazeDecoder(data_e)
	reply = BlazeFuncs.BlazePacket("0802","0001",packet.packetID,"1000")
	
	while (self.GAMEOBJ.Name == None):
		print "WAITING FOR NAME"
		continue
	
	#battlepackFile = open('Users/'+self.GAMEOBJ.Name+'/battlepacks.txt', 'r')
   	#battlepacks = json.loads(battlepackFile.readline())
	#battlepackFile.close()
	battlepackFile = loadMySql(self.GAMEOBJ.Name, "battlepacks")
	battlepacks = json.loads(battlepackFile)
	
	#SCAT 0 = ALL
	#SCAT 1
	#SCAT 2
	#SCAT 3 = AWARDED
	
	if len(battlepacks) > 0:
		#No multi-array/list support yet!
		reply.append("c2ccf4040304")
		reply.writeArray("ITLI")
		for i in range(len(battlepacks)):
			if len(battlepacks[i][1]) == 0:
				reply.writeArray_String("")
			else:
				continue
			reply.writeBuildArray("String")
			reply.writeInt("PID ", (i+1))
			reply.writeString("PKEY", battlepacks[i][0])
			reply.writeInt("SCAT", 3)
			reply.writeInt("UID ", self.GAMEOBJ.UserID)
			reply.append("00")
	
	self.transport.getHandle().sendall(reply.build().decode('Hex'))
	
def openPack(self, data_e):
	packet = BlazeFuncs.BlazeDecoder(data_e)

	packID = (int(packet.getVar("PID "))-1)

	#battlepackFile = open('Users/'+self.GAMEOBJ.Name+'/battlepacks.txt', 'r')
   	#battlepacks = json.loads(battlepackFile.readline())
	#battlepackFile.close()
	battlepackFile = loadMySql(self.GAMEOBJ.Name, "battlepacks")
	battlepacks = json.loads(battlepackFile)

	with open('Data/items.txt', 'r') as itemFile:
		itemDB = itemFile.readlines()
	#itemFile = open('Users/'+self.GAMEOBJ.Name+'/items.txt', 'r')
	#items = itemFile.readlines()
	#itemFile.close()
	items = loadMySql(self.GAMEOBJ.Name, "items")

	#2223 (2224-1) = End of actual item list, the rest is battlepacks
	packItems = []

	#Select random item amount
	bpItemAmt = randint(2,5)
	for i in range(bpItemAmt):
		#XP Boosts
		if (i < bpItemAmt):
			xpChance = randint(1,100)
			if(xpChance >= 95):
				packItems.append("ulte_boost_200");
			elif(xpChance >= 90):
				packItems.append("ulte_boost_100");
			elif(xpChance >= 85):
				packItems.append("ulte_boost_50");
			elif(xpChance >= 75):
				packItems.append("ulte_boost_25");

			if (xpChance >= 75):
				bpItemAmt -= 1
				continue;

		# Check if item limit reached
		if (len(items) >= 2223):
			break

		#Add always new items
		itemID = None
		while itemID is None:
			selectedItem = itemDB[randint(0,2223)].strip()
			if selectedItem not in items:
				itemID = selectedItem

		packItems.append(itemID)

		if itemID not in items:
			#itemFile.write(itemID+"\n")
			items = items+itemID+"\n"

	writeMySql(self.GAMEOBJ.Name, items, "items")
	#itemFile.close()

	battlepacks[packID][1] = packItems;

	#battlepackFile = open('Users/'+self.GAMEOBJ.Name+'/battlepacks.txt', 'w')
	#battlepackFile.write(json.dumps(battlepacks))
	#battlepackFile.close()
	writeMySql(self.GAMEOBJ.Name, json.dumps(battlepacks), "battlepacks")


	#consumeableFile = open('Users/'+self.GAMEOBJ.Name+'/consumables.txt', 'r')
	#consumeables = json.loads(consumeableFile.readline())
	#consumeableFile.close()
	consumeableFile = loadMySql(self.GAMEOBJ.Name, "consumables")
	consumeables = json.loads(consumeableFile)

	for packItem in packItems:
		if packItem == "ulte_boost_100":
			consumeables[2][1] = consumeables[2][1] + 1
		elif packItem == "ulte_boost_200":
			consumeables[3][1] = consumeables[3][1] + 1


		elif packItem == "ulte_boost_25":
			consumeables[0][1] = consumeables[0][1] + 1
		elif packItem == "ulte_boost_50":
			consumeables[1][1] = consumeables[1][1] + 1
	#consumeableFile = open('Users/'+self.GAMEOBJ.Name+'/consumables.txt', 'w')
	#consumeableFile.write(json.dumps(consumeables))
	#consumeableFile.close()
	writeMySql(self.GAMEOBJ.Name, json.dumps(consumeables), "consumables")


	reply = BlazeFuncs.BlazePacket("0802","0004",packet.packetID,"1000")
	reply.writeArray("ITLI")
	for packItem_ in packItems:
		reply.writeArray_String(packItem_)
	reply.writeBuildArray("String")

	reply.writeInt("PID ", (packID+1))
	reply.writeString("PKEY", battlepacks[packID][0])
	reply.writeInt("SCAT", 3)
	reply.writeInt("TGEN", int(time.time()))
	reply.writeInt("TVAL", int(time.time()))
	reply.writeInt("UID ", self.GAMEOBJ.UserID)

	self.transport.getHandle().sendall(reply.build().decode('Hex'))

	reply = BlazeFuncs.BlazePacket("0802","000a","0000","2000")
	reply.writeArray("ITLI")
	for packItem__ in packItems:
		reply.writeArray_String(packItem__)
	reply.writeBuildArray("String")

	reply.writeInt("PID ", (packID+1))
	reply.writeString("PKEY", battlepacks[packID][0])
	reply.writeInt("SCAT", 3)
	reply.writeInt("TGEN", int(time.time()))
	reply.writeInt("TVAL", int(time.time()))
	reply.writeInt("UID ", self.GAMEOBJ.UserID)
	pack1, pack2 = reply.build()
	self.transport.getHandle().sendall(pack1.decode('Hex'))
	self.transport.getHandle().sendall(pack2.decode('Hex'))

	if self.GAMEOBJ.CurServer != None:
		self.GAMEOBJ.CurServer.NetworkInt.getHandle().sendall(pack1.decode('Hex'))
		self.GAMEOBJ.CurServer.NetworkInt.getHandle().sendall(pack2.decode('Hex'))

def ReciveComponent(self,func,data_e):
	func = (str(func).upper()).strip()
	if func == '0001':
		print("[PACKS CLIENT] Get Packs")
		getPacks(self,data_e)
	elif func == '0004':
		print("[PACKS CLIENT] Open Pack")
		openPack(self,data_e)
	else:
		print(f"[INV CLIENT] ERROR! UNKNOWN FUNC {func}")
		
def loadMySql(user, field):
	#Query example: SELECT usersettings FROM `users` WHERE username = 'StoCazzo' 
	
	db = sqlite3.connect(Globals.dbDatabase) 

	cursor = db.cursor()

	sql = "SELECT "+str(field)+" FROM `users` WHERE username = '"+str(user)+"'"
	
	try:
	   cursor.execute(sql)
	   results = cursor.fetchall()
	   for row in results:
		  returnData = row[0]
		  return returnData
	except:
	   print "[SQLite] Can't load field: " + str(field) + " user: " + str(user) + " from SQLite!"

	db.close()
	
def writeMySql(user, data, field):
	#Query Example: UPDATE `users` SET `usersettings` = 'helloguys' WHERE `users`.`username` = 'StoCazzo'
	
	db = sqlite3.connect(Globals.dbDatabase) 

	cursor = db.cursor()

	sql = "UPDATE `users` SET `"+str(field)+"` = '"+str(data)+"' WHERE `users`.`username` = '"+str(user)+"'"
		
	try:
	   cursor.execute(sql)
	   db.commit()
	except:
	   print "[SQLite] Can't write field: " + str(field) + " and data: " + str(data) + " to SQLite!"
	   db.rollback()

	db.close()
