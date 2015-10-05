from ..net.protocol import CreateAccount, Withdraw, Deposit, CheckBalance

import zmq
import os.path
import sys

class ProtocolBank(BaseBank):
    def __init__(self, addr, port, keys):
        self.ctx = zmq.Context.instance()
        self.sock = ctx.socket(zmq.REQ)
        self.sock.setsockopt(zmq.RCVTIMEO, 10000)
        self.sock.connect('tcp://%s:%d:'%(addr, port))

        self.keys = keys

    def process_request(self, handler, *args):
        s = handler.send_req(*args)
        to_send = s.finish()
        tracker = self.sock.send(to_send, track=True)
        if not util.check_for_timeout(tracker):
            raise IOError('Send timed out')

        try:
            r = ReadPacket(self.sock.recv())
        except zmq.ZMQError as e:
            raise IOError('Recv timed out')
        r.verify_or_raise()

        return handler.recv_res(s, r, self.keys)

    def create_account(self, name, balance):
        return self.process_request(CreateAccount(), name, balance)

    def deposit(self, name, keycard, amount):
        return self.process_request(Deposit(), name, keycard, amount)

    def withdraw(self, name, keycard, amount):
        return self.process_request(Withdraw(), name, keycard, amount)

    def check_balance(self, name, keycard):
        return self.process_request(Deposit(), name, keycard)
