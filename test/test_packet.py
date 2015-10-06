from bibifi.net.packet import *

from unittest.mock import Mock, MagicMock
import pytest

import socket
import Crypto.PublicKey.RSA
import Crypto.Hash.SHA512
import Crypto.Signature.PKCS1_PSS

xf = pytest.mark.xfail

@pytest.fixture(scope='session')
def rsa_key():
    return Crypto.PublicKey.RSA.generate(2048)

@pytest.fixture
def sha512():
    return Crypto.Hash.SHA512.new()

@pytest.fixture(scope='session')
def signer(rsa_key):
    return Crypto.Signature.PKCS1_PSS.new(rsa_key)

def multi_side_effect(*args):
    effects = iter(args)

    def effect(*args):
        cur = next(effects)
        if isinstance(cur, Exception):
            raise cur
        elif callable(cur):
            return cur(*args)
        else:
            return cur

    return effect

def fill_buffer(values):
    def filler(buf):
        size = min(len(buf), len(values))
        buf[:size] = values[:size]
        return size
    return filler

def generate_data(length):
    return bytes(x * 3773 % 256 for x in range(0, length))

class TestReadPacket:
    def test_under_4(self):
        mock = Mock()
        mock.recv_into.side_effect = multi_side_effect(
            fill_buffer(b'aaa'),
            socket.timeout(),
        )
        with pytest.raises(socket.timeout) as execinfo:
            read_packet(mock)

    @pytest.mark.parametrize('outer_size,inner_size,data_size', [
        (0xffffffff, 4, 5000),      # too big for buffer
        (5008, 4, 5000),            # too big for buffer
        (300, 4, 50),               # outer too big
        (9, 2, 1),
        (20, 4, 50),                # outer too small
        (6, 0, -2),                 # under 8 characters
        (2, 0, -6),                 # under 4 characters
        (58, 500, 50),              # inner too big
        (58, 51, 50),               # inner too big
    ])
    def test_bad_packet_sizes(self, outer_size, inner_size, data_size):
        mock = Mock()

        sizes_packed = struct.pack('>II', outer_size, inner_size)
        data = generate_data(data_size)
        to_send = sizes_packed[:8+data_size] + data

        mock.recv_into.side_effect = multi_side_effect(
            fill_buffer(to_send),
            socket.timeout(),
        )
        with pytest.raises(IOError) as execinfo:
            read_packet(mock)

    @pytest.mark.parametrize('outer_size,inner_size,data_size', [
        (64, 30, 56),
        (8, 0, 0),
        (16, 0, 8),
        (17, 0, 9),
        (16, 8, 8),
        (17, 9, 9),
        (17, 8, 9),
        (16, 5, 8),
        (4000, 50, 3992),
        (9, 1, 1),
        (9, 0, 1),
    ])
    def test_good_packet_sizes(self, outer_size, inner_size, data_size):
        mock = Mock()

        sizes_packed = struct.pack('>II', outer_size, inner_size)
        data = generate_data(data_size)
        to_send = sizes_packed[:8+data_size] + data

        mock.recv_into.side_effect = multi_side_effect(
            fill_buffer(to_send),
            socket.timeout(),
        )

        p = read_packet(mock)

        assert p.inner_size == inner_size
        assert p.outer_size == outer_size
        assert len(p.data) == inner_size
        assert len(p.signature) == outer_size - inner_size - 8
        assert p.data == data[:inner_size]
        assert p.signature == data[inner_size:]

    @pytest.mark.parametrize('outer_size,inner_size,reads', [
        (64, 56, [56, True]),
        xf((64, 56, [57])),
        (64, 56, [10]),
        (64, 56, [10, 46, True]),
        (64, 56, [1] * 56 + [True]),
        xf((64, 56, [10, True])),
        (64, 50, [10]*5+[True]),
        (64, 50, [50, True]),
        xf((64, 50, [56])),
        xf((64, 50, [56, True])),
        (64, 0, [True]),
        xf((64, 0, [1])),
        (64, 0, [0, 0, True]),
        (9, 1, [1, 0, 0, True]),
    ])
    def test_read(self, outer_size, inner_size, reads):
        sizes = struct.pack('>II', outer_size, inner_size)
        data = generate_data(outer_size - 8)

        p = ReadPacket(sizes+data)
        loc = 0

        for read in reads:
            if type(read) == bool and read:
                p.assert_at_end()
            else:
                assert data[loc:loc+read] == p.read(read)
                loc += read

    @pytest.mark.parametrize('data,result', [
        (b'\x01', 1),
        (b'\x00', 0),
        (b'\x05\x37', 0x537),
        (b'\x00\x00\x00\x00', 0),
        (b'\x15\x20\x00\x00\x00\x00', 0x152000000000),
        (b'\x01\x00\x00\x00\x00\x00\x00\x00\x00', 0x10000000000000000),
    ])
    def test_read_number(self, data, result):
        p = ReadPacket(struct.pack('>II', len(data)+8, len(data)) + data)

        assert p.read_number(len(data)) == result
        p.assert_at_end()

    @pytest.mark.parametrize('size,length', [
        (0, 0),
        (1, 1),
        xf((0, 1)),
        (5, 5),
        (300, 300),
        xf((150, 100)),
        xf((300, 400)),
        xf((250, 0)),
    ])
    def test_read_bytes(self, size, length):
        sizes = struct.pack('>III', length+12, length+4, size)
        data = generate_data(length)
        p = ReadPacket(sizes+data)

        assert p.read_bytes() == data
        p.assert_at_end()

    @pytest.mark.parametrize('data,dollars,cents', [
        xf((b'a', 0, 0)),
        xf((b'\x00'*10, 0, 0)),
        (b'\x00\x00\x00\x00\x00\x00\x00\x00\x00', 0, 0),
        (b'\x00\x00\x00\x00\x00\x00\x00\x00\x01', 0, 1),
        (b'\x00\x00\x00\x00\x00\x00\x00\x00\xff', 2, 55),
        (b'\x00\x00\x00\x00\x00\x00\x00\x00\x63', 0, 99),
        (b'\x00\x00\x00\x00\x00\x00\x00\x01\x00', 1, 0),
        (b'\x10\x00\x00\x00\x00\x00\x00\x00\x00', 0x1000000000000000, 0),
        (b'\x00\x00\x00\x00\x35\x21\x00\x00\x23', 0x35210000, 0x23),
    ])
    def test_read_currency(self, data, dollars, cents):
        sizes = struct.pack('>II', len(data)+8, len(data))
        p = ReadPacket(sizes+data)

        c = p.read_currency()

        assert c.dollars == dollars
        assert c.cents == cents
        p.assert_at_end()

    def test_verify_good_signature(self, rsa_key, signer, sha512):
        data = generate_data(50)
        sha512.update(data)
        signature = signer.sign(sha512)

        sizes = struct.pack('>II', len(data)+len(signature)+8, len(data))

        p = ReadPacket(sizes+data+signature)

        assert p.get_data() == data
        p.verify_or_raise(rsa_key.publickey())

    def test_verify_bad_signature(self, rsa_key):
        data = generate_data(50)
        signature = b'a'*32

        sizes = struct.pack('>II', len(data)+len(signature)+8, len(data))

        p = ReadPacket(sizes+data+signature)
        assert p.get_data() == data

        with pytest.raises(IOError):
            p.verify_or_raise(rsa_key.publickey())

    def test_verify_bad_key(self, signer, sha512):
        data = generate_data(50)
        sha512.update(data)
        signature = signer.sign(sha512)

        sizes = struct.pack('>II', len(data)+len(signature)+8, len(data))

        p = ReadPacket(sizes+data+signature)

        assert p.get_data() == data

        new_key = Crypto.PublicKey.RSA.generate(2048)

        with pytest.raises(IOError):
            p.verify_or_raise(new_key.publickey())
