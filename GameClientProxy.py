import socket
import sys, traceback
import time 
import json 
import threading

DEBUG = 1
SERVER_IP = '10.0.0.117'
SERVER_PORT = 12346
BUFFER_SIZE = 1024
EOR = b'255' #end of response

def pdebug(msg):
	if(DEBUG):
		print("DEBUG:" + msg)

"""
Functional Threaded Server Client Prototype with multi client command/control and broadcast
capabilities. This is incremental foundation building to allow multi-player client server with primary 
goal of learning Python more deeply for myself 

Author : Neelesh Kamkolkar
"""

# Client Proxy class - allows send/receive capabiltiy with server hiding the complexities 
# of byte array to custom protocol of using dicts for data and command/control
class ClientProxy:

	def __init__(self, ip, port):
		pdebug(f"ClientProxy.__init__ (ip:port) ({ip}:{port})")
		self.ip = ip
		self.port = port
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((self.ip, self.port))
		self.CONNECTED = True 
	

	def set_ip(self, ip):
		self.ip = ip 

	def set_port(self, port):
		self.port = port 

	def set_connected(self, val):
		self.CONNECTED = val 

	def get_connected(self):
		return self.CONNECTED

	def get_addr(self):
		return (self.ip, self.port)

	def get_socket(self):
		return self.sock

	def client_send(self,message):
		print(f"client_send.enter: {time.ctime(time.time())}")
		message = json.dumps(message).encode('utf-8')
		print(f"client_send.message: {message} + message.type : {type(message)}\n")
		try:
			self.sock.sendall(message)
		except Exception as e:
			raise e
		#pdebug("client_send.response_from_server: %s\n" % response)
		self.client_recv()

	def client_recv(self):
		try:
			response = self.sock.recv(1024)
			print("client_recv.response_from_server: %s\n" % response)
			
			"""
			Stackover flow suggestion on byte array parsing
			arr = b'\xe0\xa6\xb8\xe0\xa6\x96 - \xe0\xa6\xb6\xe0\xa6\x96\n'
			splt = arr.decode().split(' - ')
			b_arr1 = splt[0].encode()
			b_arr2 = splt[1].encode()
		
			print(f"client_recv.response: {response}\n length : {len(response)} type: {type(response)}")
				
			#check if broadcast: 
		
			"""
			#response = json.loads(response.decode('utf-8'))

		except Exception as e:
			print(f"client_recv.response: {response}\n length : {len(response)}")
			print(f"error reading server response")
			raise e


if __name__ == "__main__":

	
	gcp1 = ClientProxy(SERVER_IP, SERVER_PORT)
	CMD = ['check_for_ready','check_for_win','update_model', 'get_model']
	i=0
	while(gcp1.get_connected() == True):
		msg = {'COMMAND' : CMD[i]}
		try:
			gcp1.client_send((msg))
			i += 1
			if(i > (len(CMD)-1)):
				i=0
				print("\n#### completed loop\n")
				time.sleep(1)
		except Exception as e: 
			print("client failed to send message to server:")
			raise e
		time.sleep(3)



	sock.close()	
	