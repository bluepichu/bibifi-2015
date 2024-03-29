from abc import ABCMeta, abstractmethod

'''
The client instantiates the communication protocol as a BaseBank and calls methods on that
The server network handler calls the methods on the implementer of BaseBank that actually stores the data

Requires valid inputs (need to be checked by calling functions)
Throw error on communication failure
Return falsy value for failed operation
Return truthy value for successful operation (possibly contents of keycard)
'''

class BaseBank(metaclass=ABCMeta):
    '''
        Rolls back the most recent transaction for the account. Only needs to store one transaction
    '''
    @abstractmethod
    def finalize(self, name, success):
        pass

    '''
    Returns True on success
    '''
    @abstractmethod
    def create_account(self, name, keycard, balance):
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
