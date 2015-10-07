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
    return Crypto.PublicKey.RSA.importKey(b'-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEAoJzjO2Nar2XAu4P6hJdhbmI+BhAwGqdOsRG+jvwR6eUl4PRU\nMFW/fMSNdcA01+bsZF6PckzjY3P6E75PPujOPGw/vQZJ3QOuIqe/yYdduHZXjOaH\nR4RHkqnDNPsHtFBhC0k8xbSBvNXZD+FCF13NbV56FW0zluonZkPYyNWG0v1I5uf7\n6gxnlTiAZe0s7NIyyL0EwE60ya7z38VEOGA/qL1Vth5KmjvV3PsBwUV4haUdnIyo\ncfyryqKBZgnQpFMow1dJAiQnvlK++PyUHQOj5TIdq3QCCtULX/IGJKMSMP+k1iCU\ng0eadOAAQUGhXzI1Zx4wLYL9QRMcDU0vO+obHQIDAQABAoIBAAaUhua++k8nTw8f\nqBrYjOBV3A6piR7+bcXpYTJAd4dqoPOnbu+QA8lb0CPb3Q5fYp32FdBsAADqFnvK\nlzqPlSt6j93xrQMGDJNU5hGenyNYjduy8iXm8Hu8wsef5T/o7yDkPj4nWA1hgYQa\nCXglmq35ae0IzU1IiJay/uWzgdORBkUkmjiFZJ1yTblqFbCjDIGBiSay+ubUkvo8\nI419SowUn6z2BlLMIuZgx65KaidMHPBYVo/YVuQYYDzl7Hw9PR/e2Lg+sJrAhH30\n+d3zptysvbFR9BsVC/Bq8wNmO0dX+NTUfWi8CsulXJq6oia8YzIEbWd9p9mZ/7SH\nwWwKeY0CgYEAuPizJ1cyIUmJjbcMLcWt2pUX+uKv3cWqejUzcEF8GT9lJG44VLIW\n51hLwS3FSRaD7PbRaVgt7ueuF46wEbc4GnAWPncwo2CGLeaTA5RxBmsbQK8sqAgE\ngjSfcuS1om67tsZsquciwSKwM0HBcQFbFSNHxViMLITPF0bCK/Tjce8CgYEA3kmn\nZlf3b+GSnUgFN7f+w+NcUsgnyuzNq6UfuIpnb5nDYgqeznN+fTMyDy5Uwt06JdRs\ngDQhzt1+oZd0T3Py+gGkVXmPOp961UsZA+g/x01Qs8pygIbaKeAzpHlNMXGs4zYA\nKlPUbEbTY1kBrZ0xbICDPJj8mVDTrG+j5vrCn7MCgYBK28PNiRltpVA4/Tq9j4IT\ns0E4NOPN0gBzYvKFXMs3gJOTUdQUWtqwF+jYrohoUudjUGRhyOEWDcdEG2ggU1Eu\nSeyGrUAO7rJ/AxC+YyX23gPygrKE8nG4rElXez4TFdN8XgN+ivpixYIfzF3YOR8+\nh7+1G2fnYHxbRDSzC3G9GwKBgC38YstDa4cTzXcITTwHrobr5E+j5MeQUcQutu9A\ngsGNt+PyeoQPVJ2mF7cYSKS/i6YD2iZzooLfQ7E+WeuN+zhJWqvsJ/tivtCdZqFu\nTLN4hTeMrD92pm9/WG+wQI34DGI866/WA94akOS+pyA5ot3lgEDrDWbSV9gWiHvi\naJ0NAoGBAJ4JLWtz3cSqFqlxuhmLbcD4VZWiHIUCwg34id2WRk9TT2aT3hfL90U0\nYZt/ExXJ9OVfS01OxdF9w1Q7+wba8leZ4DMth0/kccN0mVsQN208wPBD7BK/eLwm\nerEECiUtyocV1Tr0qoadmEdFFDZu8m8yaOqpgWG7Mpu89KP6q+oL\n-----END RSA PRIVATE KEY-----')

@pytest.fixture(scope='session')
def bad_rsa_key():
    return Crypto.PublicKey.RSA.importKey(b'-----BEGIN RSA PRIVATE KEY-----\nMIIEpQIBAAKCAQEA7UPs8UdVk+jFZG/2SaOreft+oZcXb3aEiCDQAGnj6QC+5vVS\nYTCWgcNBnS82/hu/XwBfSdhgVQdOau/82IBrCPPD41qBKxa8cqPgaz9JxW9iKmPB\nhdGALWgzn5zl0sH3dZUkgD4euMFsIEtF06lkHyAopDxRQ7VoayrTBShllrgRdzJ1\n45qs4SfKghB3l8a14UljkUU+gVc74MN2kp+fCElgngxi699LUCQAyQQ2CCfpeHxk\nUmGTBCtXJUA1MAsr/87cHfNogkjgPJTQBuwBzySYKmWzF4J8azA0Ikyb9QQuBHFL\nJRktzeWwLo1PRmKy0lCuvrkD1qXRGuLsKbuaYQIDAQABAoIBAQC6wwQIrHEFe22d\ncLA6KPY6j6ePBMKyv2T1TnbMTI3VA/xBCows6rUeMZc9ZkPwY+EQo9dd5k91vsmQ\nTZYGyZb3NgJUvRH92+i8iJiHcwrbuaBY46sabd1qYKJ6GmOhsYLbcGmJ9Nvz7HTz\nOq0dPjIMeiDjnoMNPAeUi+INJk5JAtihEV+OXyEn7T6nj97ChbgIUtwh6Gs+SXo5\noP9lXoBayfC3cqbFT5C12AXS8UOkFf0pKPxppvmSl9yWG4nyJtaeQf/X/rUWPe9F\na9Bq6gs84RyzWnmiPCezPId4KCrw+B7Ciz4332b2isikxq4z5TBB0NZUejv8cAUE\nS5P8M3U9AoGBAO127Oh73odnrr5nBC1FoNVVkbiCqGXCPQ+qvziNIuXH1HGgF3Rl\ncSpHW8y4+M1X3y0C+3KKK7n4vxgjsEl/PFV9Yz5TlmkiLPMQy6CFcAyoRnUjJBzk\nZyxdLeTPQ6n9DicVkvZnM4/2MaHIFYd3f9QJvHv+H2m/+V/QL2bWHXZbAoGBAP/J\nBPFObsnYx8tOcSGpSC4Zb9GpVJobP0UNfeSEIWZ52z9oQaaYELH2OUFpdVILA+Km\nS06Y6ndrcJ3/jUAmGPV1xJaepV16uQqTtb5K+pg8CnqQemW6Ozya0tH+Rb7BSLVf\nCmTnb1OVi2/1xej5fgHCVesT2RMntbXROLPmlGbzAoGAMMu+VOuXR6XDn7aVgiQL\nr6rcvdiDeB2Y5I5Gqv09jZAplIu8JhvuTCzLrV7ZKYEECEDToK7J23ZE9lXnFMND\nh6GzcgxFHSd7qxrpbPvekYtGpy1ob1Nz7AbdtmXs1pJ8hQWG5IFCdDO38TGnUuX4\na37wr14B4H4lZU3nX69h8H8CgYEA7kvYzvbDQEk12bK6syGCnXAVPL8Eko3P5AUt\nxDdU5qOgHvKCNzJ0W1eI/+e/5S9d70n93ruXtKnjwU7TyW+00PlmrOwgI3ax7aiv\nKRmxXSKSoJz5asyVY2DaB8lcMNrhYhepF1iF3tjzjtrqBqJpQjpK0TcshSv5nenN\naczndQECgYEApvTWT9hiEeZpVmxgWlxdqxsWwxYXJXoAT3FcW4wMjPXeJ1eCtezz\nFenivNKed6teg4WTuhDkQiib9an9ozlfkcyZU06BVyxYfuLTAv6zbXyDS7wFNaRC\nGId6Bnn+gtyfAmy7VrOHk596XZvbGSneOsige6nKmgwtBKkfnsRrRN0=\n-----END RSA PRIVATE KEY-----')

@pytest.fixture
def sha512():
    return Crypto.Hash.SHA512.new()

@pytest.fixture(scope='session')
def bad_signer(bad_rsa_key):
    return Crypto.Signature.PKCS1_PSS.new(bad_rsa_key)    

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

    def test_verify_bad_key(self, bad_rsa_key, signer, sha512):
        data = generate_data(50)
        sha512.update(data)
        signature = signer.sign(sha512)

        sizes = struct.pack('>II', len(data)+len(signature)+8, len(data))

        p = ReadPacket(sizes+data+signature)

        assert p.get_data() == data

        with pytest.raises(IOError):
            p.verify_or_raise(bad_rsa_key.publickey())

class TestWritePacket:
    @pytest.mark.parametrize('data', [
        ([b'hello', b'world']),
        ([b'5034']*20),
        ([]),
        ([b'',b'hi']),
        ([b'']),
    ])
    def test_write(self, data):
        p = WritePacket()
        for datum in data:
            p.write(datum)
        assert p.get_data() == b''.join(data)

    @pytest.mark.parametrize('number,size,result', [
        (15, 2, b'\x00\x0f'),
        (0x342241, 7, b'\x00\x00\x00\x00\x34\x22\x41'),
        (0, 5, b'\x00\x00\x00\x00\x00'),
        (0x121212121212121212121212121212, 16, b'\x00' + b'\x12'*15),
    ])
    def test_write_number(self, number, size, result):
        p = WritePacket()
        p.write_number(number, size)
        assert p.get_data() == result

    @pytest.mark.parametrize('number,size', [
        (132412342342, 3),
        (-5, 3),
        (-1, 4),
        (1000, 1),
        (256, 1),
        (65546, 2),
    ])
    def test_write_invalid_number(self, number, size):
        p = WritePacket()
        with pytest.raises(IOError):
            p.write_number(number, size)

    @pytest.mark.parametrize('data', [
        (None),
        (b'sdfj'),
        (generate_data(234)),
        (b'a'),
    ])
    def test_write_bytes(self, data):
        data = data or b''
        p = WritePacket()
        size = struct.pack('>I', len(data))

        p.write_bytes(data)
        assert p.get_data() == size + data

    def test_finish(self, rsa_key, signer, sha512):
        data = generate_data(50)
        presign = struct.pack('>I', len(data)) + data

        sha512.update(presign)

        p = WritePacket()
        p.write(data)
        finished = p.finish(rsa_key)

        assert signer.verify(sha512, finished[len(data)+8:])

    def test_finish_bad_key(self, bad_rsa_key, signer, sha512):
        data = generate_data(50)

        p = WritePacket()
        p.write(data)
        finished = p.finish(bad_rsa_key)

        presign = struct.pack('>I', len(data)) + data
        sha512.update(presign)

        try:
            assert not signer.verify(sha512, finished[len(data)+8:])
        except:
            pass
