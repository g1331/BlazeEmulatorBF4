import Utils.BlazeFuncs as BlazeFuncs


def ReciveComponent(self,func,data_e):
	func = func.upper()
	if func == '0032':
		print("[0801] ECHO")
		packet = BlazeFuncs.BlazeDecoder(data_e)
		reply = BlazeFuncs.BlazePacket("0801","0032",packet.packetID,"3000")
		self.transport.getHandle().sendall(reply.build().decode('Hex'))
	else:
		print(f"[0801] ERROR! UNKNOWN FUNC {func}")
		
#0000 0801 0032 4002 3000 0006
#0016 0004 0074 0000 2000 0000
