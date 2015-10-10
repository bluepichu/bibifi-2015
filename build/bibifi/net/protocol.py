from abc import ABCMeta, abstractmethod

from .util import generate_nonce
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA512, SHA
from bibifi.validation import validate_name, validate_file, validate_currency
from bibifi.net.packet import WritePacket

class ProtocolMethod(metaclass=ABCMeta):
    def make_packet(self):
        p = WritePacket()
        p.write_number(method_types[self.name], 1)
        return p

    def generate_digest(self, s, r):
        nonce = generate_nonce()

        hasher = SHA.new()
        hasher.update(nonce)
        hasher.update(s.get_data())

        r.write_bytes(nonce)
        r.write_bytes(hasher.digest())

    def validate_digest(self, s, r):
        nonce = r.read_bytes()
        digest = r.read_bytes()

        hasher = SHA.new()
        hasher.update(nonce)
        hasher.update(s.get_data())

        if hasher.digest() != digest:
            raise IOError('Invalid response digest')

    @abstractmethod
    def send_req(self, *args):
        pass

    @abstractmethod
    def recv_req(self, s):
        pass

    @abstractmethod
    def send_res(self, s, result):
        pass

    @abstractmethod
    def recv_res(self, s, r):
        pass

class Transaction(ProtocolMethod):
    def send_req(self, name, keycard, amount):
        s = self.make_packet()
        s.write_string(name)
        s.write_bytes(keycard)
        s.write_currency(amount)
        return s

    def recv_req(self, s):
        name = s.read_string()
        keycard = s.read_bytes()
        amount = s.read_currency()
        s.assert_at_end()

        valid = validate_name(name) and validate_currency(amount, overflow=True)

        return valid, (name, keycard, amount)

    def send_res(self, s, success):
        r = self.make_packet()
        if success:
            r.write_number(1, 1)
        else:
            r.write_number(0, 1)

        self.generate_digest(s, r)
        return r

    def recv_res(self, s, r):
        success = r.read_number(1)

        self.validate_digest(s, r)
        r.assert_at_end()

        return bool(success)

class CreateAccount(Transaction):
    name = 'create_account'

class Deposit(Transaction):
    name = 'deposit'

class Withdraw(Transaction):
    name = 'withdraw'

class CheckBalance(ProtocolMethod):
    name = 'check_balance'

    def send_req(self, name, keycard):
        s = self.make_packet()
        s.write_string(name)
        s.write_bytes(keycard)
        return s

    def recv_req(self, s):
        name = s.read_string()
        keycard = s.read_bytes()
        s.assert_at_end()

        valid = validate_name(name)

        return valid, (name, keycard)

    def send_res(self, s, balance):
        r = self.make_packet()

        if balance:
            r.write_number(1, 1)
            r.write_currency(balance)
        else:
            r.write_number(0, 1)
        
        self.generate_digest(s, r)

        return r

    def recv_res(self, s, r):
        success = r.read_number(1)
        balance = None

        if success:
            balance = r.read_currency()

        self.validate_digest(s, r)
        r.assert_at_end()

        return balance

methods = [None, CreateAccount(), Deposit(), Withdraw(), CheckBalance()]
method_types = dict((x.name, i) for i, x in enumerate(methods) if x)
