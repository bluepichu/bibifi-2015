# TODO implement bank

from bibifi.basebank import BaseBank
from abc import ABCMeta, abstractmethod

class Bank(BaseBank):
    def __init__(self):
        pass

    '''
    Rolls back the most recent transaction for the account. Only needs to store one transaction
    '''
    @abstractmethod
    def rollback(self, name):
        pass

    '''
    Returns keycard contents to be saved
    '''
    @abstractmethod
    def create_account(self, name, balance):
        pass

    '''
    Returns True on success
    '''
    @abstractmethod
    def deposit(self, name, keycard, amount):
        pass

    '''
    Return True on success
    '''
    @abstractmethod
    def withdraw(self, name, keycard, amount):
        pass

    '''
    Returns balance (Currency) on success
    '''
    @abstractmethod
    def check_balance(self, name, keycard):
        pass
