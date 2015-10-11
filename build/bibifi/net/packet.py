import struct
from Crypto.Hash import SHA512
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto import Random
from bibifi.currency import Currency

aes_key_size = 24
aes_block_size = AES.block_size
magic = b'cdb2'

def read_packet(sock, key):
    data = bytearray(4096)
    data_view = memoryview(data)
    count = 0
    while count < 4:
        read_count = sock.recv_into(data_view[count:])
        if read_count == 0: raise IOError('Peer disconnected')
        count += read_count
    outer_size, = struct.unpack('>I', data[:4])
    if outer_size > 4000:
        raise IOError('Packet too big')
    while count < outer_size:
        read_count = sock.recv_into(data_view[count:])
        if read_count == 0: raise IOError('Peer disconnected')
        count += read_count
    return ReadPacket(bytes(data_view[:count]), key)

class ReadPacket:
    def __init__(self, data, key):
        if len(data) < 8 + aes_block_size:
            raise IOError('Packet too small')
        self.outer_size, encsize = struct.unpack('>II', data[:8])
        enc = data[8:][:encsize]
        iv = data[8+encsize:][:aes_block_size]
        eaeskey = data[8+encsize+aes_block_size:]

        rsa = PKCS1_OAEP.new(key)
        aeskey = rsa.decrypt(eaeskey)

        aes = AES.new(aeskey, AES.MODE_CFB, iv)
        plain = aes.decrypt(enc)

        if plain[:len(magic)] != magic:
            raise IOError('Decryption failed')

        self.data = plain[len(magic):]
        self.inner_size = len(self.data)
        self.ptr = 0

    def read(self, count):
        if self.ptr + count > self.inner_size:
            raise IOError('Packet underflow')

        start = self.ptr
        self.ptr += count
        end = self.ptr

        return self.data[start:end]

    def read_bytes(self):
        count, = struct.unpack('>I', self.read(4))
        return self.read(count)

    def read_string(self, encoding='utf-8'):
        return self.read_bytes().decode(encoding)

    def read_number(self, size):
        data = self.read(size)
        number = 0
        for b in data:
            number = number << 8 | b
        return number

    def read_currency(self):
        return Currency(dollars=self.read_number(8), cents=self.read_number(1))

    def get_data(self):
        return self.data

    def assert_at_end(self):
        if self.ptr != self.inner_size:
            raise IOError('Packet too large')

    def verify_or_raise(self, key):
        pass

class WritePacket:
    def __init__(self):
        self.data_create = []

    def write(self, data):
        self.data_create.append(data)

    def write_number(self, value, size):
        if value < 0:
            raise IOError('Cannot encode negative value')
        if value >= 1 << 8*size:
            raise IOError('Number too large')
        self.write(bytes((value >> (size-i-1)*8)&0xff for i in range(size)))

    def write_bytes(self, data):
        self.write(struct.pack('>I', len(data)))
        self.write(data)

    def write_string(self, s, encoding='utf-8'):
        self.write_bytes(s.encode(encoding))

    def write_currency(self, c):
        self.write_number(c.dollars, 8)
        self.write_number(c.cents, 1)

    def get_data(self):
        return b''.join(self.data_create)

    def finish(self, key):
        data = self.get_data()

        rand = Random.new()

        aeskey = rand.read(aes_key_size)
        iv = rand.read(aes_block_size)
        aes = AES.new(aeskey, AES.MODE_CFB, iv)
        rsa = PKCS1_OAEP.new(key)

        eaeskey = rsa.encrypt(aeskey)
        message = aes.encrypt(magic + data)

        sizes = struct.pack('>II', len(message) + len(iv) + len(eaeskey) + 8, len(message))
        return sizes + message + iv + eaeskey
