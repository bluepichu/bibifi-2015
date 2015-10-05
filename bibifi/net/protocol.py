from enum import Enum, unique

from .util import generate_nonce
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA512, SHA

class ProtocolMethod:
    def make_packet(self):
        p = WritePacket()
        p.write_number(methods_types[self.name], 1)
        return p

    def generate_digest(self, s, r):
        nonce = generate_nonce()

        hasher = SHA.new()
        hasher.update(nonce)
        hasher.update(s.get_data())

        r.write_bytes(nonce)
        r.write_bytes(hasher.digest())

    def validate_digest(self, s, r):
        nonce = r.get_bytes()
        digest = r.get_bytes()

        hasher = SHA.new()
        hasher.update(nonce)
        hasher.update(s.get_data())

        if hasher.digest() != digest:
            raise IOError('Invalid response digest')

class CreateAccount(ProtocolMethod):
    name = 'create_account'

    def send_req(self, name, balance):
        s = self.make_packet()
        s.write_bytes(name)
        s.write_currency(balance)
        return s

    def serv(self, bank, s, keys):
        name = s.read_bytes()
        balance = s.read_currency()
        s.assert_at_end()

        valid = validate_name(name) and validate_currency(balance, overflow=True)

        keycard = valid and bank.create_account(name, balance)

        r = self.make_packet()
        if keycard:
            r.write_number(1, 1)
            cipher = PKCS1_OAEP.new(keys.atm)
            r.write_bytes(cipher.encrypt(keycard))
        else:
            r.write_number(0, 1)

        self.generate_digest(s, r)

        return r

    def recv_res(self, s, r, keys):
        success = r.read_number(1)
        keycard = None

        if success:
            keycard_cipher = r.read_bytes()
            cipher = PKCS1_OAEP.new(keys.atm)
            keycard = cipher.decrypt(keycard_cipher)

        self.validate_digest(s, r)
        r.assert_at_end()

        return keycard

def Transaction(ProtocolMethod):
    def send_req(self, name, keycard, amount):
        s = self.make_packet()
        s.write_bytes(name)
        s.write_bytes(keycard)
        s.write_currency(amount)
        return s

    def serv(self, bank, s, keys):
        name = s.read_bytes()
        keycard = s.read_bytes()
        amount = s.read_currency()
        s.assert_at_end()

        valid = validate_name(name) and validate_currency(amount, overflow=True)
        success = valid and self.handle_bank(bank, name, keycard, amount)

        r = self.make_packet()
        if success:
            r.write_number(1, 1)
        else:
            r.write_number(0, 1)

        self.generate_digest(s, r)
        return r

    def recv_res(self, s, r, keys):
        success = r.read_number(1)

        self.validate_digest()
        r.assert_at_end()

        return bool(success)

def Deposit(Transaction):
    name = 'deposit'

    def handle_bank(self, bank, *args):
        bank.deposit(*args)

def Withdraw(Transaction):
    name = 'withdraw'

    def handle_bank(self, bank, *args):
        bank.withdraw(*args)

def CheckBalance(ProtocolMethod):
    name = 'check_balance'

    def send_req(self, name, keycard):
        s = self.make_packet()
        s.write_bytes(name)
        s.write_bytes(keycard)
        return s

    def serv(self, bank, s, keys):
        name = s.read_bytes()
        keycard = s.read_bytes()
        s.assert_at_end()

        valid = validate_name(name)
        balance = valid and bank.check_balance(name, keycard)

        r = self.make_packet()

        if balance:
            r.write_number(1, 1)
            r.write_currency(balance)
        else:
            r.write_number(0, 1)
        
        self.generate_digest(s, r)

        return r

    def recv_res(self, s, r, keys):
        success = r.read_number(1)
        balance = None

        if success:
            balance = r.read_currency()

        self.validate_digest(s, r)
        r.assert_at_end()

        return balance

methods = [None, CreateAccount(), Deposit(), Withdraw(), CheckBalance()]
method_types = dict((x.name, i) for i, x in enumerate(methods))