from bibifi.net.protocol import *
from bibifi.net import protocol

import pytest
from test.conftest import *
from unittest.mock import Mock

import struct
from bibifi.currency import Currency
from bibifi.net.packet import ReadPacket, WritePacket

class ProtocolMethodSample(ProtocolMethod):
    name = 'sample'

    def send_req(self, *args): pass
    def recv_req(self, s): pass
    def send_res(self, s, result, keys): pass
    def recv_res(self, s, r, keys): pass

@pytest.fixture
def protocol_sample():
    samp = ProtocolMethodSample()
    samp.method_type = 0xff
    protocol.method_types[samp.name] = samp.method_type

    return samp

def create_read_packet(data):
    return ReadPacket(struct.pack('>II', len(data)+8, len(data)) + data)

def test_make_packet(protocol_sample):
    p = protocol_sample.make_packet()
    assert p.get_data() == struct.pack('>B', protocol_sample.method_type)

# TODO improve testing of digest
def test_digest(protocol_sample):
    s = create_read_packet(generate_data(64))

    rw = WritePacket()
    protocol_sample.generate_digest(s, rw)
    rr = create_read_packet(rw.get_data())
    protocol_sample.validate_digest(s, rr)

@pytest.fixture(params=[CreateAccount, Withdraw, Deposit, CheckBalance])
def protocol_method(request):
    return request.param()

@pytest.fixture
def protocol_method_request_args(request, protocol_method):
    names = ['hello', 'hi', 'bluepichu', 'Strikeskids', 'a'*500, 'bleh']
    currencies = [Currency(50, 50), Currency(0, 0), Currency(234, 17), Currency(18, 34), Currency(2341, 79), Currency(342, 1234)]
    keycards = [b'a', b'keycard', b'a'*500, b'keycard2', b'thisisasecret', generate_data(50)]
    if not 0 <= request.param < len(names):
        return
    i = request.param
    if protocol_method.name in {'create_account', 'withdraw', 'deposit'}:
        return (names[i], keycards[i], currencies[i])
    elif protocol_method.name == 'check_balance':
        return (names[i], keycards[i])

@pytest.fixture
def protocol_method_return_value(request, protocol_method):
    args = []
    if protocol_method.name in {'create_account', 'withdraw', 'deposit'}:
        args = [False, True]
    elif protocol_method.name == 'check_balance':
        args = [Currency(50, 50), Currency(0, 0), Currency(234, 17), Currency(18, 34), Currency(2341, 79), Currency(342, 1234)]

    if 0 <= request.param < len(args):
        return args[request.param]

@pytest.mark.parametrize('protocol_method_request_args', list(range(6)), indirect=['protocol_method_request_args'])
def test_request(protocol_method, protocol_method_request_args):
    if protocol_method_request_args == None:
        return
    args = protocol_method_request_args
    s = protocol_method.send_req(*args)

    sr = create_read_packet(s.get_data())
    assert sr.read_number(1) == protocol.method_types[protocol_method.name]

    _, results = protocol_method.recv_req(sr)
    assert results == tuple(args)

@pytest.mark.parametrize('protocol_method_return_value', list(range(6)), indirect=['protocol_method_return_value'])
def test_response(protocol_method, protocol_method_return_value):
    if protocol_method_return_value == None:
        return
    s = create_read_packet(generate_data(64))

    r = protocol_method.send_res(s, protocol_method_return_value)

    rr = create_read_packet(r.get_data())
    assert rr.read_number(1) == protocol.method_types[protocol_method.name]

    result = protocol_method.recv_res(s, rr)
    assert not protocol_method_return_value and not result or protocol_method_return_value == result

