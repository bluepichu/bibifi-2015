import socket
import threading
import socketserver
import sys
import signal
import traceback

from queue import Queue

from bibifi.net.packet import read_packet
from bibifi.net import protocol
from bibifi.bank.bankhandler import BankRequestStage, BankRequest

class ThreadedHandler(socketserver.BaseRequestHandler):
    def __init__(self, handler, auth_keys, *args):
        self.result_queue = Queue(maxsize=1)
        self.finished = False
        self.handler = handler
        self.auth_keys = auth_keys
        self.finish_type = None

        super().__init__(*args)

    @classmethod
    def initializer_with_args(cls, *args):
        def init(*pargs):
            return cls(*(args + pargs))
        return init

    def bank_request(self, type, data, stage):
        self.handler.request(BankRequest(self, type, data, stage))

    def read_packet(self):
        return read_packet(self.request, self.auth_keys.bank)

    def get_method(self, req_packet):
        packet_type = req_packet.read_number(1)

        if 0 < packet_type < len(protocol.methods):
            return protocol.methods[packet_type]
        else:
            raise IOError('Invalid method')

    def send_bank(self, method, data):
        self.bank_request(method.name, data, BankRequestStage.start)
        self.finish_type = BankRequestStage.finish_success

    def recv_bank(self):
        return self.result_queue.get()

    def send_packet(self, res_packet):
        self.request.sendall(res_packet.finish(self.auth_keys.atm))

    def handle(self):
        self.request.settimeout(10)
        method = None
        data = None
        started = False
        try:
            req_packet = self.read_packet()
            method = self.get_method(req_packet)

            valid, data = method.recv_req(req_packet)

            if valid:
                self.send_bank(method, data)
                started = True
                req_packet.verify_or_raise(self.auth_keys.atm)
                result = self.recv_bank()
            else:
                result = False

            res_packet = method.send_res(req_packet, result)
            self.send_packet(res_packet)
        except IOError as e:
            print('protocol_error')
            traceback.print_exc(file=sys.stderr)
            sys.stdout.flush()
            self.finish_type = BankRequestStage.finish_fail
        finally:
            try:
                self.request.shutdown(socket.SHUT_RDWR)
                self.request.close()
            except:
                traceback.print_exc(file=sys.stderr)
            self.finished = True
            if self.finish_type != None and started and method:
                self.bank_request(method.name, data, self.finish_type)

class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

def listen(host, port, bank_handler, auth_keys):
    server = ThreadedServer((host, port),
        ThreadedHandler.initializer_with_args(bank_handler, auth_keys))
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    def handle_terminate():
        server.shutdown()
        server.server_close()

    return handle_terminate
