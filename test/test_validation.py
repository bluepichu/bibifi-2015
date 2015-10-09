from bibifi.validation import *

import pytest
from unittest.mock import Mock

@pytest.mark.parametrize("succeed,inp", [
    (True, "127.0.0.1"),
    (True, "241.242.255.250"),
    (True, "0.0.0.0"),
    (True, "12.34.56.78"),
    (True, "99.100.255.0"),
    (True, "1.2.3.4"),
    (False, "00.1.2.3"),
    (False, "256.0.0.0"),
    (False, "1"),
    (False, "123.234.345.456"),
    (False, "1.1.1.1.1"),
    (False, "1...1"),
    (False, "0.0.0.123456")
])
def test_ip_validation(succeed, inp):
    assert bool(validate_ip(inp)) == succeed

@pytest.mark.parametrize("succeed,inp", [
    (True, 1024),
    (True, 2048),
    (True, 12345),
    (True, 65535),
    (True, 9876),
    (True, 4325),
    (True, 11111),
    (True, 8080),
    (True, 1337),
    (False, 0),
    (False, 1023),
    (False, 80),
    (False, 65536),
    (False, 111111),
    (False, -123),
    (False, 22),
    (False, 23),
    (False, 4294967295)
])
def test_port_validation(succeed, inp):
    assert bool(validate_port(inp)) == succeed

@pytest.mark.parametrize("succeed,inp", [
    (True, "thebestaccountname"),
    (True, "ted"),
    (True, "."),
    (True, ".."),
    (True, "..."),
    (True, "hyphens-are-fun.txt"),
    (True, "__init__.py"),
    (True, "101"),
    (True, "id_rsa"),
    (True, "a" * 250),
    (False, "Ted"),
    (False, "who uses spaces"),
    (False, "/bin/sh"),
    (False, ""), # >:(
    (False, "\x00"),
    (False, "åß∂ƒ©˙∆˚¬"),
    (False, "a" * 251)
])
def test_name_validation(succeed, inp):
    assert bool(validate_name(inp)) == succeed

@pytest.mark.parametrize("succeed,inp", [
    (True, "ted.card"),
    (True, "bank.auth"),
    (True, "account.txt"),
    (True, "a" * 255),
    (True, "hyphens-are-fun.txt"),
    (True, ".a"),
    (True, "..a"),
    (True, "__init__.py"),
    (True, "101"),
    (True, "id_rsa"),
    (False, "Ted"),
    (False, "who uses spaces"),
    (False, "/bin/sh"),
    (False, ""),
    (False, "\x00"),
    (False, "åß∂ƒ©˙∆˚¬"),
    (False, "a" * 256),
    (False, "."),
    (False, "..")
])
def test_file_validation(succeed, inp):
    assert bool(validate_file(inp)) == succeed
