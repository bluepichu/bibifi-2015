import struct
from Crypto.Hash import SHA512
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Signature import PKCS1_PSS
from Crypto import Random
from bibifi.currency import Currency

def read_packet(sock, pem):
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
    return ReadPacket(bytes(data_view[:count]), pem)

class ReadPacket:
    def __init__(self, data, pem):

        off = 256+4+16

        self.pem = pem
        if len(data) < off+8:
            raise IOError('Packet too small')
        self.outer_size, = struct.unpack('>I', data[:4])
        self.iv = data[4:20]
        eaeskey = data[20:off]
        enc = data[off:]
        cipher = PKCS1_OAEP.new(pem)
        self.aeskey = cipher.decrypt(eaeskey)

        cipher = AES.new(self.aeskey, AES.MODE_CFB, self.iv)
        packet = cipher.decrypt(enc)
        
        self.inner_size, = struct.unpack('>I', packet[:4])

        if self.inner_size > len(packet)-4:
            raise IOError('Invalid packet size')
        self.data = packet[4:self.inner_size+4]
        self.signature = packet[self.inner_size+4:]
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
        h = SHA512.new()
        h.update(self.data)
        signer = PKCS1_PSS.new(key)
        try:
            if not signer.verify(h, self.signature):
                raise IOError('Invalid packet signature')
        except ValueError:
            raise IOError('Invalid packet signature')

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

    def finish(self, signkey, enckey):
        data = self.get_data()

        h = SHA512.new()
        h.update(data)
        signer = PKCS1_PSS.new(signkey)
        sig = signer.sign(h)

        packet = struct.pack('>I', len(data)) + data + sig
        
        aeskey = Random.new().read(24)

        cipher = PKCS1_OAEP.new(enckey)
        header = cipher.encrypt(aeskey)

        iv = Random.new().read(AES.block_size)

        cipher = AES.new(aeskey, AES.MODE_CFB, iv)
        body = cipher.encrypt(packet)

        return struct.pack('>I', len(header)+len(body))+iv+header+body

