import socket
import threading
import socketserver

import bibifi.net.packet as packet
import bibifi.net.protocol as protocol

class ThreadedHandler(socketserver.BaseRequestHandler):	
	def handle(self):
		print("Incoming");
		parse_packet = packet.read_packet(self.request)
		packet_type = parse_packet.read_number(4)
		if packet_type > 0 and packet_type < len(protocol.methods):
			method = protocol.methods[packet_type];
		else:
			#???
			return;
		valid, data = method.recv_req(parse_packet);
		print(valid, data);

class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass

def listen(host, port):
	print("Listening");
	server = ThreadedServer((host, port), ThreadedHandler)
	server_thread = threading.Thread(target = server.serve_forever)
	server_thread.daemon = True
	server_thread.start()

if __name__ == "__main__":
	listen("127.0.0.1", 3000)
	while (True):
		pass
