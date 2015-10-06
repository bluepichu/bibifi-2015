from bibifi.net.packet import *

from unittest.mock import Mock, MagicMock
import pytest

import socket

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
        buf[0:len(values)] = values
        return len(values)
    return filler

class TestReadPacketMethod:
    def test_under_4(self):
        mock = Mock()
        mock.recv_into.side_effect = multi_side_effect(
            fill_buffer(b'aaa'),
            socket.timeout(),
        )
        with pytest.raises(socket.timeout) as execinfo:
            read_packet(mock)

    def test_large_packet(self):
        mock = Mock()
        mock.recv_into.side_effect = multi_side_effect(
            fill_buffer(struct.pack('>I', 0xffffffff)),
            fill_buffer(b'a'*50),
            socket.timeout(),
        )
        with pytest.raises(IOError) as execinfo:
            read_packet(mock)

class ReadPacketTest:
    pass