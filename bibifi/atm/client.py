from bibifi.atm.protocolbank import ProtocolBank
from bibifi import argparser, validation
import sys

def main():
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
		args = parser.parse_args()
	except Exception as err:
		print_error(err)
		print_error("Exiting with code 255...")
		exit(255)

	if not args.c:
		args.c = args.a + ".card"

	validation.validate_bank_auth_file(args.s)
	validation.validate_ip(args.i)
	validation.validate_port(args.p)
	validation.validate_card_file(args.c)
	validation.validate_name(args.a)

	bank = ProtocolBank(args.i, args.p, args.s)

	if args.n:
		amount = validate_numeric_input(args.n)
		if not amount or amount.dollars < 10:
			print_error("Invalid amount specified.")
			print_error("Exiting with code 255...")
			exit(255)
		bank.deposit(args.a, args.c, amount)
	elif args.d:
		amount = validate_numeric_input(args.d)
		if not amount or (amount.dollars == 0 and amount.cents == 0):
			print_error("Invalid amount specified.")
			print_error("Exiting with code 255...")
			exit(255)
		bank.deposit(args.a, args.c, amount)
	elif args.w:
		amount = validate_numeric_input(args.w)
		if not amount or (amount.dollars == 0 and amount.cents == 0):
			print_error("Invalid amount specified.")
			print_error("Exiting with code 255...")
			exit(255)
		bank.widthdraw(args.a, args.c, amount)
	elif args.g:
		bank.check_balance(args.a, args.c)
	else:
		exit(255) # ???

def print_error(*objs):
    print(*objs, file=sys.stderr)

if __name__ == "__main__":
	main()