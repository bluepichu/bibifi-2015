from bibifi.bank import banksocket, bankhandler
from bibifi.authfile import Keys

def main():
    try:
        # TODO read cl arguments
        # TODO validate cl arguments

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
