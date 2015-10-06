from bibifi.net.packet import *

from unittest.mock import Mock, MagicMock
import pytest

import socket

xf = pytest.mark.xfail

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
        data = b'a'*max(0, data_size)
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
        data = bytes(x * 3773 % 256 for x in range(0, data_size))
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
        data = bytes(x * 3773 % 256 for x in range(0, outer_size - 8))

        p = ReadPacket(sizes+data)
        loc = 0

        for read in reads:
            if type(read) == bool and read:
                p.assert_at_end()
            else:
                assert data[loc:loc+read] == p.read(read)
                loc += read

