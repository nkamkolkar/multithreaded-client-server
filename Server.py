import socket, time, sys, traceback 
import threading
import socketserver
import pprint
import GameClientProxy as GCP
import json 

"""
Functional Threaded Server Client Prototype with multi client command/control and broadcast
capabilities
This is incremental foundation building to allow multi-player client server with primary 
goal of learning Python more deeply for myself 
Author : Neelesh Kamkolkar
"""

SERVER_IP = '10.0.0.117' # your server ip address
SERVER_PORT = 12346
BUFFER_SIZE = 1024
EOR = b'255' #end of response

clientCount = 0  # global reference count for clients
CLIENTS = [] 	 # global list of client sockets
shared_message = {'SERVER_BROADCAST' : 'Message'}  #shared message buffer

threadLock = threading.Lock()

DEBUG = 1 #debug flag
def pdebug(msg):
	if(DEBUG):
		print("DEBUG:" + msg)


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
	
	"""
	The most important learning for me (not in docs) was that the
	BaseRequestHandler is instantiated ONCE per client. I used to keep 
	losing sockets and i couldn't figure out why until I ran across a great post
	on stackover flow explaining this. 
	
	The 'while 1' in this methond is important to maintain the socket between
	client server 

	"""
	def handle(self):
		while 1: 
			data = self.request.recv(1024)
			data = json.loads(data.decode('utf-8'))
			#Each client is updating shared state on server
			#use a lock for crtical section
			threadLock.acquire(1)
			#process server command handles the bytes to dict conversions
			response = self.server.process_server_commands(data)
			threadLock.release()
			self.request.sendall(response)



class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):

	#Over ride get_request so we can track the client sockets
	#There were no examples on internet showing this for doing
	#Broadcasts across multiple clients using TCP
	def get_request(self):
		pdebug("get_request")
		try:
			client, addr = self.socket.accept()
			global clientCount # global reference count for clients
			global CLIENTS     # global list of client sockets
			clientCount += 1 
			pdebug("clientCount " + str(clientCount))
			if(client not in CLIENTS):
				CLIENTS.append((client,addr))
				#print(f"Added new client from: {client}")
		except socket.error as msg: 
			msg = "GameServer.get_request: " + msg
			pdebug(msg)

		return(client, addr)

	def broadcast(self, a_dict):
		global clientCount
		global CLIENTS
		for client, address in CLIENTS: 
			try:
				#append the client address to the broad cast message 
				#client can verify with it's own copy or ignore
				a_dict['client_address'] = address
				msg = json.dumps(a_dict).encode('utf-8')
				client.sendall(msg)
			except Exception as e:
				#This client died or closed connection, remove the client socket from list
				#and decrement reference count
				CLIENTS.remove((client, address))
				client.close()
				clientCount -= 1 
				pass


	def process_server_commands(self, client_data):
		if(client_data is None):
			return 
		
		pdebug("process_server_commands " + str(client_data))
		#just convert the command to UPPPER case for now and add server response
		shared_message = str(client_data['COMMAND']).upper()
		client_data['SERVER_RESPONSE'] = shared_message
		
		"""
		end_of_cmd = {"EOR" : "EOR"}
		client_data = str(client_data) + str(end_of_cmd)
		#client_data = bytes(client_data.encode())
		print(f"client_data_merged: {client_data}")
		response = client_data
		"""

		response = json.dumps(client_data).encode('utf-8')
		
		#Server responses and broad cast messages can get interleaved in asych setup
		#I need a way to distinguish them on the client side 
		#using a end of response byte for this(EOR won't be used outside of the delimeter) 
		pdebug("AFTER process_server_commands " + str(response))
		return response


if __name__ == "__main__":

	#create a threaded TCP server with a request handler which is instantiated for each client
	server = ThreadedTCPServer((SERVER_IP, SERVER_PORT), ThreadedTCPRequestHandler)
	ip, port = server.server_address

	# Start a thread with the server -- that thread will then start one
    # more thread for each request
	server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
	server_thread.setDaemon(True)
	server_thread.start()
	print("Server main loop running in thread:", server_thread.getName())

	#Server simply broadcasts the shared buffer to all clients. 
	#TODO: Brodcast only when there is something new
	while True:
		print(f"Clients:\n {CLIENTS}\n******")
		server.broadcast(shared_message)
		time.sleep(5)

	server.shutdown()
