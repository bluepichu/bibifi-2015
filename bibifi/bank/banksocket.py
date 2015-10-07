import socket
import threading
import socketserver
import sys
import signal

from queue import Queue

from bibifi.net.packet import read_packet
from bibifi.net import protocol
from bibifi.bank.bankhandler import BankRequestStage, BankRequest

class ThreadedHandler(socketserver.BaseRequestHandler):
    def __init__(self, handler, auth_keys):
        self.result_queue = Queue(max_size=1)
        self.finished = False
        self.handler = handler
        self.auth_keys = auth_keys

    @classmethod
    def initializer_with_args(cls, *args):
        def init():
            return cls(*args)
        return init

    def bank_request(self, type, data, stage):
        self.handler.requests.push(BankRequest(self, type, data, stage))

    def handle(self):
        finish = None
        try:
            req_packet = read_packet(self.request)
            packet_type = req_packet.read_number(1)

            if 0 < packet_type < len(protocol.methods):
                method = protocol.methods[packet_type]
            else:
                raise IOError('Invalid method')

            valid, data = method.recv_req(req_packet)

            if valid:
                req_packet.verify_or_raise()

                self.bank_request(method.name, data, BankRequestStage.start)
                finish = BankRequestStage.finish_success
                result = self.result_queue.get()
            else:
                result = False

            res_packet = method.send_res(req_packet, result, self.auth_keys)
            self.request.sendall(res_packet.finish())
        except IOError as e:
            print('protocol_error')
            print(e, file=sys.stderr)
            sys.stdout.flush()
            self.request.close()
            finish = BankRequestStage.finish_fail
        else:
            self.finished = True
            if finish != None:
                self.bank_request(method.name, data, finish)

class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def listen(host, port, bank_handler, auth_keys):
    server = ThreadedServer((host, port),
        ThreadedHandler.initializer_with_args(bank_handler, auth_keys))
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    def handle_terminate():
        server_thread.stop()

    return handle_terminate
