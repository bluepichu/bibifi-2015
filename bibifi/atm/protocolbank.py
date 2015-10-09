from bibifi.net.protocol import CreateAccount, Withdraw, Deposit, CheckBalance
from bibifi.net.packet import read_packet
from bibifi.basebank import BaseBank
from bibifi.authfile import Keys
import socket
import os.path
import sys
import json


class ProtocolBank(BaseBank):
    def __init__(self, host, port, keys):
        self.sock = socket.create_connection((host, port))
        self.sock.settimeout(10)
        self.key_file = keys
        self.keys = Keys.load_from_file(self.key_file)

    def process_request(self, handler, *args):
        s = handler.send_req(*args)
        self.sock.sendall(s.finish(self.keys.atm))
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

    def rollback(self, name): #MISSING!
        print("ERROR ATTEMPTING TO USE UNDECLARED FUNCTION ROLLBACK");
        pass
