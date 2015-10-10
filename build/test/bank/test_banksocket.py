from bibifi.bank.banksocket import *
from bibifi.bank import banksocket

import pytest
from unittest.mock import Mock, patch

from bibifi.bank.bankhandler import BankRequestStage, BankRequest

@pytest.fixture
def threaded_handler(keys):
    handler = Mock()
    with patch('builtins.super'):
        return handler, ThreadedHandler(handler, keys, None, None, None)

@pytest.mark.parametrize('success,number', [
    (True, 1),
    (True, 2),
    (True, 4),
    (False, 5),
    (False, 0),
    (False, -10),
    (False, 30)
])
def test_get_method(threaded_handler, number, success):
    bank, handler = threaded_handler
    mock = Mock()
    mock.read_number.return_value = number
    try:
        with patch('bibifi.bank.banksocket.protocol.methods', list(range(5))):
            result = handler.get_method(mock)
            assert success
            assert result == number
    except IOError:
        assert not success
    except Exception:
        raise

def test_send_bank(threaded_handler):
    u1, u2 = 123238472384, 32431234
    class SpecialMethod: name = u1
    bank, handler = threaded_handler

    handler.send_bank(SpecialMethod(), u2)
    bank.requests.put.assert_called_with(BankRequest(handler, u1, u2, BankRequestStage.start))
    assert handler.finish_type == BankRequestStage.finish_success

def test_recv_bank(threaded_handler):
    _, handler = threaded_handler
    u = 2348884803

    handler.result_queue.put(u)
    assert handler.recv_bank() == u

def test_send_packet(threaded_handler):
    _, handler = threaded_handler
    req = Mock()
    rp = Mock()
    handler.request = req
    handler.send_packet(rp)
    req.sendall.assert_called_with(rp.finish())

def test_send_packet_exception(threaded_handler):
    _, handler = threaded_handler
    req = Mock()
    req.sendall.side_effect = IOError('Timed out')
    rp = Mock()
    handler.request = req
    try:
        handler.send_packet(rp)
        assert False
    except IOError:
        req.sendall.assert_called_with(rp.finish())

def test_handle_valid():
    main = Mock()
    data, res_packet, req_packet = 72374234, 323412343, Mock()
    method = Mock()
    main.read_packet.return_value = req_packet
    main.get_method.return_value = method
    method.recv_req.return_value = (True, data)
    method.send_res.return_value = res_packet

    ThreadedHandler.handle(main)

    assert main.read_packet.called
    main.get_method.assert_called_once_with(req_packet)
    method.recv_req.assert_called_once_with(req_packet)
    main.send_bank.assert_called_once_with(method, data)
    req_packet.verify_or_raise.assert_called_once_with(main.auth_keys.atm)
    main.recv_bank.assert_called_once_with()
    assert method.send_res.called
    main.send_packet.assert_called_once_with(res_packet)

def test_handle_throws(capsys):
    main = Mock()
    data, res_packet, req_packet = 72374234, 323412343, Mock()
    method = Mock()
    main.read_packet.return_value = req_packet
    main.get_method.return_value = method
    method.recv_req.return_value = (True, data)
    method.send_res.return_value = res_packet
    main.send_packet.side_effect = IOError('Failed')

    ThreadedHandler.handle(main)

    assert main.read_packet.called
    main.get_method.assert_called_once_with(req_packet)
    method.recv_req.assert_called_once_with(req_packet)
    main.send_bank.assert_called_once_with(method, data)
    req_packet.verify_or_raise.assert_called_once_with(main.auth_keys.atm)
    main.recv_bank.assert_called_once_with()
    assert method.send_res.called
    main.send_packet.assert_called_once_with(res_packet)
    main.bank_request.assert_called_with(method.name, data, BankRequestStage.finish_fail)

    out, err = capsys.readouterr()
    assert out == 'protocol_error\n'
