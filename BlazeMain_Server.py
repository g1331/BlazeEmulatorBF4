import sqlite3
import threading

from twisted.internet import reactor, ssl
from twisted.internet.protocol import Factory, Protocol
from twisted.protocols.policies import TimeoutMixin

import Utils.BlazeFuncs as BlazeFuncs
import Utils.DataClass as DataClass
import Utils.Globals as Globals
from Components_Server import Authentication as Auth
##from Components import Authentication as Auth, Util, Game, UserSessions as UsrSe, Unknown
from Components_Server import Clubs, Game
from Components_Server import GameReporting as GameRpt
from Components_Server import Inventory, Packs, Stats, Unknown
from Components_Server import UserSessions as UserSe
from Components_Server import Util


class BLAZEHUB(Protocol, TimeoutMixin):
	
	def setTcpKeepAlive(self, enabled):
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, enabled)
		
	def timeoutConnection(self):
		print "[BLAZE Server] ConKilled (TimeOut)"
		#self.transport.loseConnection()

	def connectionMade(self):
		#self.transport.setTcpNoDelay(True)
		self.setTimeout(600)
		self.GAMEOBJ = None
		self.DATABUFF = ""
		self.transport.setTcpKeepAlive(True)
		if self.GAMEOBJ == None:
			self.GAMEOBJ = DataClass.BF3Server()
			self.GAMEOBJ.NetworkInt = self.transport
			Globals.Servers.append(self.GAMEOBJ)
			print "[BLAZE Server] GameOBJ Made"
		print "[BLAZE Server] ConMade"

	def connectionLost(self, reason):
		print "[BLAZE Server] ConLost"
		if self.GAMEOBJ != None:
			self.GAMEOBJ.IsUp = False
			
		print('[SQLite] Deleting server table server: ' + str(self.GAMEOBJ.GameName))

		db = sqlite3.connect(Globals.dbDatabase) 

		cursor = db.cursor()

	
		#cursor.execute("DELETE FROM `" + Globals.dbDatabase + "`.`serverslist` WHERE `serverslist`.`name` = '" + str(self.GAMEOBJ.GameName) + "'")
		cursor.execute("DELETE FROM `serverslist` WHERE `serverslist`.`name` = '" + str(self.GAMEOBJ.GameName) + "'")
	
	
		db.commit()
		cursor.close()
		db.close()

		print("[SQLite] Server table deleted!")

	def readConnectionLost(self, reason):
		print "[BLAZE Server] readConLost"
		if self.GAMEOBJ != None:
			self.GAMEOBJ.IsUp = False
			
		self.transport.loseConnection()
		
	def writeConnectionLost(self, reason):
		print "[BLAZE Server] writeConLost"
		if self.GAMEOBJ != None:
			self.GAMEOBJ.IsUp = False
			
		self.transport.loseConnection()

	def dataReceived(self, data):
		self.resetTimeout()
		data_e = data.encode('hex')
		allData = False

		if len(self.DATABUFF) != 0 and self.DATABUFF != data_e:
			self.DATABUFF = self.DATABUFF+data_e
			data_e = self.DATABUFF

		dataLenghth = (int(data_e[:4], 16)*2)+28
		if len(data_e) >= dataLenghth:
			if len(self.DATABUFF) != 0:
				self.DATABUFF = ""
			allData = True
			data_1 = data_e[:dataLenghth]
			data_2 = data_e[dataLenghth:]

			if len(data_2) > 0:
				self.dataReceived(data_2.decode('Hex'))
		elif self.DATABUFF == "":
			self.DATABUFF = data_e

		if allData:
			packet = BlazeFuncs.BlazeDecoder(data_1)
			if packet.packetComponent == '0001':
				Auth.ReciveComponent(self,packet.packetCommand,data_e)
			elif packet.packetComponent == '0004':
				Game.ReciveComponent(self,packet.packetCommand,data_e)
			elif packet.packetComponent == '0007':
				Stats.ReciveComponent(self,packet.packetCommand,data_e)
			elif packet.packetComponent == '0009':
				Util.ReciveComponent(self,packet.packetCommand,data_e)
			elif packet.packetComponent == '001c':
				GameRpt.ReciveComponent(self,packet.packetCommand,data_e)
			elif packet.packetComponent == '7802':
				UserSe.ReciveComponent(self,packet.packetCommand,data_e)
			elif packet.packetComponent == '0801':
				Unknown.ReciveComponent(self,packet.packetCommand,data_e)
			elif packet.packetComponent == '0802':
				Packs.ReciveComponent(self,packet.packetCommand,data_e)
			elif packet.packetComponent == '0803':
				Inventory.ReciveComponent(self,packet.packetCommand,data_e)
			elif packet.packetComponent == '000b':
				Clubs.ReciveComponent(self,packet.packetCommand,data_e)
			else:
				print(
					f"[BLAZE SERVER] ERROR!! Unhandled Comonent({packet.packetComponent}) and Function({packet.packetCommand})"
				)
