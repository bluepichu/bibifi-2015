# TODO implement bank

from bibifi.basebank import BaseBank

class Bank(BaseBank):
    def __init__(self):
        pass

    '''
    Rolls back the most recent transaction for the account. Only needs to store one transaction
    '''
    def rollback(self, name):
        raise NotImplementedError()

    '''
    Returns keycard contents to be saved
    '''
    def create_account(self, name, balance):
        raise NotImplementedError()

    '''
    Returns True on success
    '''
    def deposit(self, name, keycard, amount):
        raise NotImplementedError()

    '''
    Return True on success
    '''
    def withdraw(self, name, keycard, amount):
        raise NotImplementedError()

    '''
    Returns balance (Currency) on success
    '''
    def check_balance(self, name, keycard):
        raise NotImplementedError()
