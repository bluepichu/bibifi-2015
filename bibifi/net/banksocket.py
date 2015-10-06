import socket
import threading
import socketserver

import packet

class ThreadedHandler(socketserver.BaseRequestHandler):	
	def handle(self):
		print("Incoming");
		parse_packet = packet.read_packet(self.request)

class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass

def listen(host, port):
	server = ThreadedServer((host, port), ThreadedHandler)
	server_thread = threading.Thread(target = server.serve_forever)
	server_thread.daemon = True
	server_thread.start()

if __name__ == "__main__":
	listen("127.0.0.1", 3000)
	print("Listening");
	while (True):
		pass
