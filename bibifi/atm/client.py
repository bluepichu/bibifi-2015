from bibifi.atm.protocolbank import ProtocolBank
from bibifi import argparser, validation

from Crypto.Random import random
from bibifi.net.packet import WritePacket
from bibifi.authfile import Keys
from bibifi.currency import Currency

import sys
import os

def main():
    args = run_parser(sys.argv[1:])

    if not validate_parameters(args):
        print_error("Invalid parameters.")
        print_error("Exiting with code 255...")
        exit(255)

    auth_keys = Keys.load_from_file(args.s)
    method = get_method(args, auth_keys)
    run_method(method)

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
    actions.add_argument("-g", action="store_true", help="Gets the balance of an account.")

    try:
        args = parser.parse_args(args)
        if not args.c: args.c = args.a + '.card'
        return args
    except Exception as err:
        print_error(err)
        print_error("Exiting with code 255...")
        exit(255)

def validate_parameters(args):
    return validation.validate_ip(args.i) and validation.validate_port(args.p) and validation.validate_name(args.a)

def load_card_file(card_file_path, create=False):
    if not validation.validate_card_file(card_file_path, exists=not create):
        print_error('Invalid card file')
        exit(255)
    try:
        if create:
            p = WritePacket()
            p.write_number(random.getrandbits(512), 64)
            card = p.get_data()
            with open(card_file_path, 'wb') as f:
                f.write(card)
            return card
        else:
            with open(card_file_path, 'rb') as f:
                return f.read()
    except Exception as e:
        print_error('Failed to get card file', e)
        exit(255)

def get_method(args, auth_keys):
    bank = ProtocolBank(args.i, args.p, auth_keys)

    if args.n:
        amount = Currency.parse(args.n)
        card = load_card_file(args.c, create=True)
        if not amount or amount.dollars < 10:
            print_error("Invalid amount.")
            exit(255)

        method = bank.create_account
        on_failure = lambda: os.remove(args.c)
    elif args.d:
        amount = Currency.parse(args.d)
        card = load_card_file(args.c)
        if not amount or (amount.dollars == 0 and amount.cents == 0):
            print_error("Invalid amount.")
            exit(255)

        method = bank.deposit
    elif args.w:
        amount = Currency.parse(args.w)
        card = load_card_file(args.c)
        if not amount or (amount.dollars == 0 and amount.cents == 0):
            print_error("Invalid amount.")
            exit(255)

        method = bank.withdraw
    elif args.g:
        amount = None
        card = load_card_file(args.c)
        method = bank.check_balance
    else:
        exit(255) # ???

    name = args.a

    if amount:
        execute = lambda: method(name, card, amount)
    else:
        execute = lambda: method(name, card)

    return execute

def run_method(method):
    try:
        result = method()
        if not result:
            raise Exception('Transaction failed')
    except IOError as e:
        if on_failure: on_failure()
        print_error(e)
        exit(63)
    except Exception as e:
        if on_failure: on_failure()
        print_error(e)
        exit(255)

def print_error(*objs):
    print(*objs, file=sys.stderr)
