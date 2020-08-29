import gnucash

from . import utils


class RawSplit(object):
    def __init__(self, account, memo, value, amount=None):
        self.memo = memo
        self.account = account
        self.value = value
        self.amount = amount

    def float_value(self):
        if self.value:
            return float(self.value)
        return 0.0

    def create_split(self, book, transaction, not_cleared=False):
        split = gnucash.Split(book)
        if self.value:
            split.SetValue(gnucash.GncNumeric(self.value))
        if self.amount:
            split.SetAmount(gnucash.GncNumeric(self.amount))
        root_acct = book.get_root_account()
        acct = utils.lookup_account(root_acct, self.account)
        split.SetAccount(acct)
        if not not_cleared:
            split.SetReconcile('c')
        split.SetParent(transaction)

    def validate(self, book=None):
        if book is not None:
            root_acct = book.get_root_account()
            acct = utils.lookup_account(root_acct, self.account)
            return acct is not None
        # always valid if no book is set
        return True


class RawTransaction(object):
    def __init__(self, date, description, commodity, splits=None):
        self.date = date
        self.description = description
        self.commodity = commodity
        self.splits = splits

    def append_split(self, split):
        if self.splits is None:
            self.splits = [split]
        else:
            self.splits.append(split)

    def validate(self, book=None):
        if self.splits is None or len(self.splits) == 0:
            return False
        if not all(split.validate(book) for split in self.splits):
            return False

        balance = 0.0
        for split in self.splits:
            balance += split.float_value()

        return abs(balance) <= 1e-9

    def create_transaction(self, book, not_cleared=False):
        comm_table = book.get_table()
        ns, symbol = [x for x in self.commodity.split(':') if x]
        commodity = comm_table.lookup(ns, symbol)
        trans = gnucash.Transaction(book)
        trans.BeginEdit()
        trans.SetDate(self.date.day, self.date.month, self.date.year)
        trans.SetCurrency(commodity)
        trans.SetDescription(self.description)

        for idx, split in enumerate(self.splits):
            split.create_split(book, trans, not_cleared=idx > 0 or not_cleared)

        trans.CommitEdit()
