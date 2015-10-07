from ..net.protocol import CreateAccount, Withdraw, Deposit, CheckBalance
from socket import socket
import os.path
import sys
from ..net.packet import read_packet

class ProtocolBank(BaseBank):
    def __init__(self, host, port, keys):
        self.sock = socket()
        self.sock.create_connection((host, port))
        self.sock.settimeout(10)
        self.keys = keys

    def process_request(self, handler, *args):
        s = handler.send_req(*args)
        self.sock.sendall(s.finish())
        r = read_packet(self.sock)
        r.verify_or_raise()
        return handler.recv_res(s, r, self.keys)

    def create_account(self, name, keycard, balance):
        return self.process_request(CreateAccount(), name, keycard, balance)

    def deposit(self, name, keycard, amount):
        return self.process_request(Deposit(), name, keycard, amount)

    def withdraw(self, name, keycard, amount):
        return self.process_request(Withdraw(), name, keycard, amount)

    def check_balance(self, name, keycard):
        return self.process_request(Deposit(), name, keycard)
