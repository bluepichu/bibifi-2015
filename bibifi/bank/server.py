from bibifi.bank import banksocket, bankhandler
from bibifi.authfile import Keys
from bibifi import validation, argparser

import sys
import signal
import traceback

def main():
    parser = argparser.ThrowingArgumentParser()
    parser.add_argument('-p', metavar='<port>', type=int, help='The port to listen on', default=3000)
    parser.add_argument("-s", metavar="<auth-file>", type=str, help="The auth file path.  (Default: bank.auth)", default="bank.auth")
    
    try:
        args = parser.parse_args()

        if not validation.validate_file(args.s) or not validation.validate_port(args.p):
            print('Invalid arguments', file=sys.stderr)
            exit(255)

        start_server(args.p, args.s)
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        exit(255)

def start_server(port, auth_file_path):
    def sigterm_hook(signum, stack_frame):
        if signum == signal.SIGINT:
            print("VERY BAD. CHANGE THIS")
        term_socket()
        term_handler()
        print('Finished terminating', file=sys.stderr)

    auth_keys = Keys.random()
    auth_keys.export_auth_file(auth_file_path)

    handler = bankhandler.BankHandler()
    term_handler = handler.termination_hook()

    signal.signal(signal.SIGTERM, sigterm_hook)
    signal.signal(signal.SIGINT, sigterm_hook)

    term_socket = banksocket.listen('0.0.0.0', port, handler, auth_keys)

    handler.serve_forever()
