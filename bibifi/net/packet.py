import struct
from Crypto.Hash import SHA512
from Crypto.Signature import PKCS1_PSS

class ReadPacket:
    def __init__(self, data):
        if len(data) < 4:
            raise IOError('Packet too small')
        self.inner_size, = struct.unpack('>I', data[:4])
        if inner_size > len(data)-4:
            raise IOError('Invalid packet size')
        self.data = data[4:self.inner_size+4]
        self.signature = data[self.inner_size+4:]
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

    def read_number(self, size):
        data = self.read(size)
        number = 0
        for b in data:
            number = number << 8 | b
        return number

    def read_currency(self):
        return Currency(self.read_number(8), self.read_number(1))

    def get_data():
        return self.data

    def assert_at_end(self):
        if self.ptr != self.inner_size:
            raise IOError('Packet too large')

    def verify_or_raise(self, key):
        h = SHA512.new()
        h.update(self.data)
        signer = PKCS1_PSS.new(key)
        if not signer.verify(h, self.signature):
            raise IOError('Invalid packet signature')

class WritePacket:
    def __init__(self):
        self.data_create = []

    def write(self, data):
        self.data_create.append(data)

    def write_number(self, value, size):
        self.write(bytes((a >> (size-i)*8) for i in range(size)))

    def write_bytes(self, data):
        self.write(struct.pack('>I', len(data)))
        self.write(data)

    def write_currency(self, c):
        self.write_number(c.dollars, 8)
        self.write_number(c.cents, 1)

    def get_data(self):
        return b''.join(self.data_create)

    def get_presign(self):
        inner = self.get_data()
        count = len(inner)
        return struct.pack('>I', count) + inner

    def finish(self, key):
        presign = self.get_presign()

        h = SHA512.new()
        h.update(presign)
        signer = PKCS1_PSS.new(key)
        sig = signer.sign(h)

        return presign + sig
