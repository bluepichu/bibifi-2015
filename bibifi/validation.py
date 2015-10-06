import re

valid_characters = re.compile(r'^[_\-\.0-9a-z]*$')
invalid_files = set(['.', '..'])

def validate_currency(c, overflow=False):
    return c.validate(overflow=overflow)

def validate_name(name):
    return 1 <= len(name) <= 250 and valid_characters.match(name) != None

def validate_file(file):
    if file in invalid_files:
        return False
    return 1 <= len(file) <= 255 and valid_characters.match(file) != None

