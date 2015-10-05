class Currency:
    def __init__(self):
        self.dollars = 0
        self.cents = 0

    def validate(self, overflow=False, cents=self.cents, dollars=self.dollars):
        if dollars < 0:
            return False
        if overflow and dollars > 4294967295:
            return False
        return 0 <= cents <= 99

    def __update(self, new_dollars, new_cents):
        if not self.validate(cents=new_cents, dollars=new_dollars):
            return False
        self.dollars = new_dollars
        self.cents = new_cents
        return True

    def add(self, c):
        added_cents = self.cents + c.cents
        new_dollars = self.dollars + c.dollars + added_cents // 100
        new_cents = added_cents % 100
        return self.__update(new_dollars, new_cents)

    def sub(self, c):
        added_cents = self.cents - c.cents
        new_dollars = self.dollars - c.dollars + added_cents // 100
        new_cents = added_cents % 100
        return self.__update(new_dollars, new_cents)
