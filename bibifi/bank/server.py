from bibifi.bank import banksocket, bankhandler
from bibifi.authfile import Keys
from bibifi import validation, argparser

import sys

def main():
    parser = argparser.ThrowingArgumentParser()
    parser.add_argument('-p', metavar='<port>', type=int, help='The port to listen on', default=3000)
    parser.add_argument("-s", metavar="<auth-file>", type=str, help="The auth file path.  (Default: bank.auth)", default="bank.auth")
    
    try:
        args = parser.parse_args()

        if not validation.validate_file(args.s) or not validation.validate_port(args.p):
            print('Invalid arguments', file=sys.stderr)
            exit(255)

        start_server(port, auth_file_path)
    except Exception as e:
        print(e, file=sys.stderr)
        exit(255)

# port and auth_file_path should be validated
def start_server(port, auth_file_path):
    def sigterm_hook():
        term_socket()
        term_handler()

    auth_keys = Keys.random()
    auth_keys.export_auth_file(auth_file_path)

    handler = bankhandler.BankHandler()
    term_handler = hander.termination_hook()

    term_socket = banksocket.listen('0.0.0.0', port, handler, auth_keys)

    handler.serve_forever()
