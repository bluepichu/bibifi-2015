from bibifi.net.util import *

import pytest

@pytest.mark.parametrize('times', [(1), (2), (3), (4)])
def test_generate_nonce(times):
    cur = generate_nonce()
    for i in range(times):
        cur, prev = generate_nonce(), cur
        assert prev != cur
