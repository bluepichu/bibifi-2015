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
        self.result_queue = Queue(maxsize=1)
        self.finished = False
        self.handler = handler
        self.auth_keys = auth_keys
        self.finish = None

    @classmethod
    def initializer_with_args(cls, *args):
        def init():
            return cls(*args)
        return init

    def bank_request(self, type, data, stage):
        self.handler.requests.push(BankRequest(self, type, data, stage))

    def read_packet():
        return read_packet(self.request)

    def get_method(self, req_packet):
        packet_type = req_packet.read_number(1)

        if 0 < packet_type < len(protocol.methods):
            return protocol.methods[packet_type]
        else:
            raise IOError('Invalid method')

    def send_bank(self, method, data):
        self.bank_request(method.name, data, BankRequestStage.start)
        self.finish = BankRequestStage.finish_success

    def recv_bank(self):
        return self.result_queue.get()

    def send_packet(self, res_packet):
        self.request.sendall(res_packet.finish())

    def handle(self):
        try:
            req_packet = self.read_packet()
            method = self.get_method(req_packet)

            valid, data = method.recv_req(req_packet)

            if valid:
                self.send_bank(method, data)
                req_packet.verify_or_raise()
                result = self.recv_bank()
            else:
                result = False

            res_packet = method.send_res(req_packet, result, self.auth_keys)
            self.send_packet(res_packet)
        except IOError as e:
            print('protocol_error')
            print(e, file=sys.stderr)
            sys.stdout.flush()
            self.request.close()
            self.finish = BankRequestStage.finish_fail
        finally:
            self.finished = True
            if self.finish != None:
                self.bank_request(method.name, data, self.finish)

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
