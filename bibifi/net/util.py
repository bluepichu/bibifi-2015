from Crypto.Random.random import getrandbits
import struct

def generate_nonce():
    bits = getrandbits(64)
    nonce = struct.pack('>Q', bits)
    return nonce

def check_for_timeout(tracker):
    try:
        tracker.wait(timeout=10)
        return True
    except NotDone as e:
        return False
