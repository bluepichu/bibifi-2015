class Currency:
    def __init__(self, dollars=0, cents=0):
        self.dollars = dollars + cents // 100
        self.cents = cents % 100

    def __validate(self, dollars, cents, overflow=False):
        if dollars < 0:
            return False
        if overflow and dollars > 4294967295:
            return False
        return 0 <= cents <= 99        

    def validate(self, overflow=False):
        return self.__validate(self.dollars, self.cents, overflow=overflow)

    def __update(self, new_dollars, new_cents):
        new_dollars = new_dollars + new_cents // 100
        new_cents = new_cents % 100
        if not self.__validate(new_dollars, new_cents):
            return False
        self.dollars = new_dollars
        self.cents = new_cents
        return True

    def add(self, c):
        return self.__update(self.dollars + c.dollars, self.cents + c.cents)

    def sub(self, c):
        return self.__update(self.dollars - c.dollars, self.cents - c.cents)

    def __str__(self):
        return '%d.%02d'%(self.dollars, self.cents)

    def __repr__(self):
        return 'Currency(dollars=%d, cents=%d)'%(self.dollars, self.cents)

    def __eq__(self, c):
        return isinstance(c, Currency) and c.dollars == self.dollars and c.cents == self.cents
