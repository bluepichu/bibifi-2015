from bibifi.net.protocol import CreateAccount, Withdraw, Deposit, CheckBalance
from bibifi.net.packet import read_packet
from socket import socket
import os.path
import sys
import json

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
        result = self.process_request(CreateAccount(), name, keycard, balance)
        if result:
            print('{"account":%s,"initial_balance":%s'%(json.dumps(name), balance))
        return result

    def deposit(self, name, keycard, amount):
        result = self.process_request(Deposit(), name, keycard, amount)
        if result:
            print('{"account":%s,"deposit":%s'%(json.dumps(name), amount))
        return result

    def withdraw(self, name, keycard, amount):
        result = self.process_request(Withdraw(), name, keycard, amount)
        if result:
            print('{"account":%s,"withdraw":%s'%(json.dumps(name), amount))
        return result

    def check_balance(self, name, keycard):
        result = self.process_request(Deposit(), name, keycard)
        if result:
            print('{"account":%s,"balance":%s'%(json.dumps(name), result))
        return result
