from Crypto.PublicKey import RSA

import os.path
import sys

class Keys:
    def __init__(self, atm_key, bank_key):
        self.atm = atm_key
        self.bank = bank_key

    @classmethod
    def random(cls, bits=2048):
        return cls(atm_key=RSA.generate(bits), bank_key=RSA.generate(bits))

    @classmethod
    def load_from_file(cls, auth_file_path):
        if not os.path.isfile(auth_file_path):
            exit(255)
        try:
            with open(auth_file_path, 'rb') as auth_file:
                keys = auth_file.read().split(b'|')
                if len(keys) != 2:
                    print('Invalid number of keys', file=sys.stderr)
                    exit(255)
                atm = RSA.importKey(keys[0])
                bank = RSA.importKey(keys[1])
                return cls(atm_key=atm, bank_key=bank)
        except Exception as e:
            print('Failed to import keys: ' + str(e), file=sys.stderr)
            exit(255)

    def export_auth_file(self, auth_file_path):
        if os.path.exists(auth_file_path):
            print('Auth file already exists', file=sys.stderr)
            exit(255)
        with open(auth_file_path, 'wb') as auth_file:
            auth_file.write(self.atm.exportKey())
            auth_file.write(b'|')
            auth_file.write(self.bank.publickey().exportKey())
            print("created")
            sys.stdout.flush()