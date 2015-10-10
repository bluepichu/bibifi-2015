from bibifi.atm.protocolbank import ProtocolBank
from bibifi import argparser, validation

from Crypto.Random import random
from bibifi.net.packet import WritePacket
from bibifi.authfile import Keys
from bibifi.currency import Currency

import sys
import os
import traceback

failure_hooks = []
failure_trace = False

def main():    
    try:
        args = run_parser(sys.argv[1:])

        if not validate_parameters(args):
            raise Exception('Invalid parameters')

        auth_keys = Keys.load_from_file(args.s)
        method = get_method(args, auth_keys)
        run_method(method)
    except IOError as e:
        handle_failure()
        exit(63)
    except Exception as e:
        handle_failure()
        exit(255)

def handle_failure():
    if failure_trace: traceback.print_exc(file=sys.stderr)
    for method in failure_hooks:
        try:
            method()
        except:
            print('Error on failure hook', file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

def run_parser(args):
    parser = argparser.ThrowingArgumentParser(description="Process atm input.")
    parser.add_argument("-s", metavar="<auth-file>", type=str, help="The bank's auth file.  (Default: bank.auth)", default="bank.auth")
    parser.add_argument("-i", metavar="<ip-address>", type=str, help="The bank's IP address.", default="127.0.0.1")
    parser.add_argument("-p", metavar="<port>", type=int, help="The bank's port.", default=3000)
    parser.add_argument("-c", metavar="<card-file>", type=str, help="The cardfile for the account.")
    parser.add_argument("-a", metavar="<account>", type=str, help="The account on which to operate", required=True)
    
    actions = parser.add_mutually_exclusive_group(required=True)

    actions.add_argument("-n", metavar="<balance>", type=str, help="Creates a new account with the given inital balance.")
    actions.add_argument("-d", metavar="<amount", help="Deposits the given amount into an account.")
    actions.add_argument("-w", metavar="<amount>", type=str, help="Withdraws the given amount from an account.")
    actions.add_argument("-g", action="count", help="Gets the balance of an account.")

    args = parser.parse_args(args)
    if not args.c: args.c = args.a + '.card'
    return args

def validate_parameters(args):
    return validation.validate_ip(args.i) and validation.validate_port(args.p) and validation.validate_name(args.a)

def load_card_file(card_file_path, create=False):
    if not validation.validate_card_file(card_file_path, exists=not create):
        raise Exception('Invalid card file')
    if create:
        p = WritePacket()
        p.write_number(random.getrandbits(512), 64)
        card = p.get_data()
        with open(card_file_path, 'wb') as f:
            failure_hooks.append(lambda: os.remove(card_file_path))
            f.write(card)
        return card
    else:
        with open(card_file_path, 'rb') as f:
            return f.read()

def get_method(args, auth_keys):
    on_failure = lambda: None
    method_name = None

    if args.n:
        amount = Currency.parse(args.n)
        card = load_card_file(args.c, create=True)
        if not amount or amount.dollars < 10:
            raise Exception('Invalid amount')

        method_name = 'create_account'
    elif args.d:
        amount = Currency.parse(args.d)
        card = load_card_file(args.c)
        if not amount or (amount.dollars == 0 and amount.cents == 0) or not amount.validate(overflow=True):
            raise Exception('Invalid amount')

        method_name = 'deposit'
    elif args.w:
        amount = Currency.parse(args.w)
        card = load_card_file(args.c)
        if not amount or (amount.dollars == 0 and amount.cents == 0) or not amount.validate(overflow=True):
            raise Exception('Invalid amount')

        method_name = 'withdraw'
    elif args.g:
        amount = None
        card = load_card_file(args.c)
        if args.g > 1:
            raise Exception("More than 1 -g flag")

        method_name = 'check_balance'
    else:
        raise ValueError('Unknown argument')

    name = args.a

    bank = ProtocolBank(args.i, args.p, auth_keys)
    method = getattr(bank, method_name)

    if amount:
        execute = lambda: method(name, card, amount)
    else:
        execute = lambda: method(name, card)

    return execute

def run_method(method):
    result = method()
    if not result:
        raise Exception('Transaction failed')

def print_error(*objs):
    print(*objs, file=sys.stderr)

