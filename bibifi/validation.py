import re
import os

valid_characters = re.compile(r'^[_\-\.0-9a-z]*$')
numeric_input_regex = re.compile(r'^(\d*)\.(\d\d)$')
ip_regex = re.compile(r'^(\d|\d\d|[01]\d\d|2([01234]\d|5[012345]))\.(\d|\d\d|[01]\d\d|2([01234]\d|5[012345]))\.(\d|\d\d|[01]\d\d|2([01234]\d|5[012345]))\.(\d|\d\d|[01]\d\d|2([01234]\d|5[012345]))$')
invalid_files = {".", ".."}

def validate_currency(c, overflow=False):
	return c.validate(overflow=overflow)

def validate_numeric_input(inp):
	match = numeric_input_regex.match(inp)

	if match:
		dollars = int(match[1])
		cents = int(match[2])

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
	return 0 < port < 65536

def validate_name(name):
	return 1 <= len(name) <= 250 and valid_characters.match(name)

def validate_file(file):
	if file in invalid_files:
		return False
	return 1 <= len(file) <= 255 and valid_characters.match(file)
