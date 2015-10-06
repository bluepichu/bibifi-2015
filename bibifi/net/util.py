from Crypto.Random.random import getrandbits
import struct

def generate_nonce():
    bits = getrandbits(64)
    nonce = struct.pack('>Q', bits)
    return nonce
