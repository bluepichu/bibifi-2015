import argparse
import re

from bibifi.currency import Currency

number_regex = re.compile(r'^[1-9]\d*$')

class ArgumentParserError(Exception):
    pass

class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)

class SingleArg(argparse.Action):
    def used(self, namespace):
        if hasattr(namespace, '__set'+self.dest):
            raise Exception('Argument %s specified multiple times'%(self.dest))
        setattr(namespace, '__set'+self.dest, True)

class ParseString(SingleArg):
    def __call__(self, parser, namespace, values, option_string=None):
        self.used(namespace)
        setattr(namespace, self.dest, values)

class ParseNumber(SingleArg):
    def __call__(self, parser, namespace, values, option_string=None):
        self.used(namespace)
        if not number_regex.match(values):
            raise ValueError('Invalid number')
        setattr(namespace, self.dest, int(values))

class StoreTrue(SingleArg):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, const=True, default=False, nargs=0, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        self.used(namespace)
        setattr(namespace, self.dest, True)

class ParseCurrency(SingleArg):
    def __call__(self, parser, namespace, values, option_string=None):
        self.used(namespace)
        result = Currency.parse(values)
        if not result:
            raise Exception('Invalid currency specified')
        setattr(namespace, self.dest, result)
