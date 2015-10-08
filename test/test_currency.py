from bibifi.currency import *

import pytest
from unittest.mock import Mock

xf = pytest.mark.xfail

@pytest.mark.parametrize('succeed,dollars,cents,overflow', [
    (True, 234234, 21, True),
    (False, 93939294319234921234, 0, True),
    (False, -1, 0, False),
    (False, 0, -1, False),
    (True, 394293429349129349234, 32, False),
    (False, 0, 100, False),
    (False, 0, 100, True),
    (False, 0, -23423, False),
    (True, 0, 0, True),
    (True, 0, 0, False),
    (True, 0, 99, True),
    (True, 0, 99, False),
])
def test_validate(succeed, dollars, cents, overflow):
    assert Currency._Currency__validate(None, dollars, cents, overflow=overflow) == succeed

@pytest.mark.parametrize('succeed,inp,out', [
    (True, (323, 23), (323, 23)),
    (True, (3, -1), (2, 99)),
    (False, (0, -1), None),
    (True, (3234234, 34), (3234234, 34)),
    (True, (10, -1000), (0, 0)),
])
def test_update(inp, out, succeed):
    c = Currency()
    result = c._Currency__update(inp[0], inp[1])
    if succeed:
        assert result
        assert c.dollars == out[0]
        assert c.cents == out[1]
    else:
        assert not result
        assert c.dollars == 0
        assert c.cents == 0

@pytest.mark.parametrize('succeed,c1,c2', [
    (True, Currency(0,0), Currency(5,10)),
    (False, Currency(0,0), Currency(-1,0)),
    (True, Currency(50, 33), Currency(500, 500)),
    (True, Currency(3423423, 34), Currency(3421, 57)),
])
def test_add(c1, c2, succeed):
    s1 = (c1.dollars, c1.cents)
    result = c1.add(c2)
    if succeed:
        assert result
        new_cents = (s1[1] + c2.cents) % 100
        new_dollars = (s1[0] + c2.dollars) + (s1[1] + c2.cents) // 100
        assert c1.dollars == new_dollars
        assert c1.cents == new_cents
    else:
        assert not result
        assert s1[0] == c1.dollars
        assert s1[1] == c1.cents

@pytest.mark.parametrize('succeed,c1,c2', [
    (False, Currency(0,0), Currency(5,10)),
    (True, Currency(0,0), Currency(-1,0)),
    (False, Currency(50, 37), Currency(500, 500)),
    (True, Currency(3423423, 34), Currency(3421, 57)),
    (True, Currency(34, 12), Currency(34, 12)),
    (True, Currency(50, 15), Currency(50, 10)),
    (True, Currency(40, 10), Currency(30, 10)),
])
def test_sub(c1, c2, succeed):
    s1 = (c1.dollars, c1.cents)
    result = c1.sub(c2)
    if succeed:
        assert result
        new_cents = (s1[1] - c2.cents) % 100
        new_dollars = (s1[0] - c2.dollars) + (s1[1] - c2.cents) // 100
        assert c1.dollars == new_dollars
        assert c1.cents == new_cents
    else:
        assert not result
        assert s1[0] == c1.dollars
        assert s1[1] == c1.cents

@pytest.mark.parametrize('c,result', [
    (Currency(0,0), '0.00'),
    (Currency(23423, 34), '23423.34'),
    (Currency(50,12), '50.12'),
    (Currency(1, 1), '1.01'),
])
def test_str(c, result):
    assert str(c) == result

@pytest.mark.parametrize('c1,c2,result', [
    (Currency(0,0),Currency(0,0),True),
    (Currency(50,12),Currency(5,10),False),
    (Currency(50,10),Currency(5,10),False),
    (Currency(5,12),Currency(5,10),False),
    (Currency(5,10),Currency(5,10),True),
])
def test_eq(c1, c2, result):
    assert (c1 == c2) == result
