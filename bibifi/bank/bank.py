import json

from bibifi.basebank import BaseBank

class Bank(BaseBank):
    def __init__(self):
        self.balances = dict()
        self.keycards = set()

    '''
    Rolls back the most recent transaction for the account. Only needs to store one transaction
    '''
    def rollback(self, name):
        if not name in self.balances: return False
        if not self.balances[name]['rollback']: return False

        function = self.balances[name]['rollback']['function']

        if function == 'create':
            self.keycards.remove(self.balances[name]['keycard'])
            del self.balances[name]

        amount = self.balances[name]['rollback']['amount']
        if function == 'deposit':
            self.withdraw(name, self.balances[name]['keycard'], amount)
        if function == 'withdraw':
            self.deposit(name, self.balances[name]['keycard'], amount)

        self.balances[name]['rollback'] = None
        return True

    '''
    Returns True on success
    '''
    def create_account(self, name, keycard, balance):
        if name in self.balances: return False
        if keycard in keycards: return False
        if balance.dollars < 10: return False
        if not balance.validate(overflow=True): return False

        self.balances[name] = dict(
            'keycard': keycard,
            'balance': balance, 
            'rollback': None)
        self.keycards.add(keycard)
        self.balances[name]['rollback'] = {'function': 'create'}

        print('{"account":%s,"initial_balance":%s'%(json.dumps(name), balance))
        return True

    '''
    Returns True on success
    '''
    def deposit(self, name, keycard, amount):
        if not name in self.balances: return False
        if self.balances[name]['keycard'] != keycard: return False
        if not amount.validate(overflow=True): return False

        result = self.balances[name]['balance'].add(amount)
        if not result: return False

        self.balances[name]['rollback'] = {'function': 'deposit', 'amount': amount}
        print('{"account":%s,"deposit":%s'%(json.dumps(name), amount))
        return True

    '''
    Return True on success
    '''
    def withdraw(self, name, keycard, amount):
        if not name in self.balances: return False
        if self.balances[name]['keycard'] != keycard: return False
        if not amount.validate(overflow=True): return False

        result = self.balances[name]['balance'].sub(amount)
        if not result: return False

        self.balances[name]['rollback'] = {'function': 'withdraw', 'amount': amount}
        print('{"account":%s,"withdraw":%s'%(json.dumps(name), amount))
        return True

    '''
    Returns balance (Currency) on success
    '''
    def check_balance(self, name, keycard):
        if not name in self.balances: return False
        if self.balances[name]['keycard'] != keycard: return False

        result = self.balances[name]['balance']
        print('{"account":%s,"balance":%s'%(json.dumps(name), result))
        return result
