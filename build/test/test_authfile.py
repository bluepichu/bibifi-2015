from bibifi.authfile import *

import pytest
from unittest.mock import Mock, patch

import tempfile
import os

@pytest.fixture(scope='session')
def auth_file_encoded_keys(rsa_key, bad_rsa_key):
    key1 = rsa_key
    key2 = bad_rsa_key.publickey()
    return (
        key1.exportKey() + b'|' + key2.exportKey(),
        key1, key2,
    )

def test_random_key():
    k = Keys.random()
    assert k.atm
    assert k.bank
    assert k.atm != k.bank

def test_load_from_file(auth_file_encoded_keys):
    auth_file_data, key1, key2 = auth_file_encoded_keys
    mock = Mock(side_effect=Exception('Exit'))
    try:
        handle, auth_file_path = tempfile.mkstemp(text=True)
        os.write(handle, auth_file_data)
        os.close(handle)
        with patch('builtins.exit', mock):
            k = Keys.load_from_file(auth_file_path)
            assert k.atm == key1
            assert k.bank == key2
    except Exception as e:
        assert e == None
    else:
        os.remove(auth_file_path)

def test_export_auth_file(auth_file_encoded_keys):
    auth_file_data, key1, key2 = auth_file_encoded_keys
    mock = Mock(side_effect=Exception('Exit'))
    try:
        handle, auth_file_path = tempfile.mkstemp()
        os.close(handle)
        os.remove(auth_file_path)
        k = Keys(key1, key2)
        with patch('builtins.exit', mock):
            k.export_auth_file(auth_file_path)
        with open(auth_file_path, 'rb') as auth_file:
            assert auth_file.read() == auth_file_data
    except Exception as e:
        assert e == None
    else:
        os.remove(auth_file_path)
