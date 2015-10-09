from bibifi.atm.client import *

import pytest
from unittest.mock import Mock, patch

from bibifi.currency import Currency
import sys
import tempfile
import os

class ChTemporaryDirectory(tempfile.TemporaryDirectory):
    def __enter__(self):
        name = super().__enter__()
        self.prev = os.getcwd()
        os.chdir(name)
        return name

    def __exit__(self, *args):
        os.chdir(self.prev)
        return super().__exit__(*args)

@pytest.mark.parametrize('error_code,argv,params', [
    (0, "-a acc -n 10.00", ('create_account', '127.0.0.1', 3000,'bank.auth', 'acc.card', False, 'acc', Currency(10,0))),
    (0, "-a bleh -d 0.01", ('deposit', '127.0.0.1', 3000,'bank.auth', 'bleh.card', True, 'bleh', Currency(0,1))),
    (0, "-a acc -w 10.00", ('withdraw', '127.0.0.1', 3000,'bank.auth', 'acc.card', True, 'acc', Currency(10,0))),
    (0, "-a acc -g", ('check_balance', '127.0.0.1', 3000,'bank.auth', 'acc.card', True, 'acc', None)),
    (0, "-aacc -n13.12", ('create_account', '127.0.0.1', 3000,'bank.auth', 'acc.card', False, 'acc', Currency(13,12))),
    (0, "-s bloop -i 15.234.12.13 -p 23413 -c bleep -a matt -n 10.00", ('create_account', '15.234.12.13', 23413,'bloop', 'bleep', False, 'matt', Currency(10,0))),
    (255, "-a acc -n 9.99", ('create_account', '127.0.0.1', 3000,'bank.auth', 'acc.card', False, 'acc', Currency(10,0))),
    (255, "-a acc -d 0.00", ('deposit', '127.0.0.1', 3000,'bank.auth', 'acc.card', False, 'acc', Currency(10,0))),
    (255, "-a acc -w 0.00", ('withdraw', '127.0.0.1', 3000,'bank.auth', 'acc.card', False, 'acc', Currency(10,0))),
])
def test_client(argv,params,keys,error_code):
    method_name, host, port, authfile, cardfile, createcard, name, amount = params
    card = b'12342384728374823718273482134'
    with ChTemporaryDirectory(), patch('bibifi.atm.client.ProtocolBank') as Bank, patch('bibifi.atm.client.sys.argv', argv.split()), patch('builtins.exit') as exiter:
        exiter.side_effect = Exception('Exited incorrectly')

        bank = Mock()
        Bank.return_value = bank
        keys.export_auth_file(authfile)
        if createcard:
            with open(cardfile, 'wb') as f:
                f.write(card)
        try:
            main()
        except Exception:
            exiter.assert_called_with(error_code)
        else:
            assert Bank.called
            assert Bank.call_args[0][:2] == (host, port)

            method_func = getattr(bank, method_name)
            assert method_func.called
            assert method_func.call_args[0][0] == name
            assert not createcard or method_func.call_args[0][1] == card
            assert not amount or method_func.call_args[0][2] == amount
            assert error_code == 0
            assert not exiter.called or exiter.call_args[0][0] == error_code
