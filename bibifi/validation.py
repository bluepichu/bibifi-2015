from bibifi.currency import Currency
import re
import os

valid_characters = re.compile(r'^[_\-\.0-9a-z]*$')
numeric_input_regex = re.compile(r'^(\d*)\.(\d\d)$')
ip_regex = re.compile(r'^(\d|[1-9]\d|1\d\d|2([01234]\d|5[012345]))\.(\d|[1-9]\d|1\d\d|2([01234]\d|5[012345]))\.(\d|[1-9]\d|1\d\d|2([01234]\d|5[012345]))\.(\d|[1-9]\d|1\d\d|2([01234]\d|5[012345]))$')
invalid_files = {".", ".."}

def validate_currency(c, overflow=False):
	return c.validate(overflow=overflow)

def validate_numeric_input(inp):
	match = numeric_input_regex.match(inp)

	if match:
		dollars = int(match.group(1))
		cents = int(match.group(2))

		amount = Currency(dollars, cents)

		if validate_currency(amount):
			return amount
	return None

def validate_bank_auth_file(file):
	if not validate_file(file):
		return False
	if not os.path.isfile(file):
		return False
	# More things probably go here...
	return True

def validate_card_file(file, exists=True):
	if not validate_file(file):
		return False
	if os.path.isfile(file) != exists:
		return False
	# More things probably go here...
	return True

def validate_ip(ip):
	return bool(ip_regex.match(ip))

def validate_port(port):
	return 1024 <= port <= 65535

def validate_name(name):
    return 1 <= len(name) <= 250 and valid_characters.match(name) != None

def validate_file(file):
    if file in invalid_files:
        return False
    return 1 <= len(file) <= 255 and valid_characters.match(file) != None

