import csv
import datetime
from enum import Enum

from . import transaction


class CSVReader(object):
    class Headers(Enum):
        DATE = 'date'
        DESC = 'description'
        ACCOUNT = 'account'
        COMMODITY = 'commodity'
        MEMO = 'memo'
        VALUE = 'value'
        AMOUNT = 'amount'

    FIELDS = tuple(item.value for item in Headers)

    def __init__(self, csvfile):
        self.reader = csv.DictReader(csvfile)

    def __iter__(self):
        trans = None
        for row in self.reader:
            if row[CSVReader.Headers.DATE.value]:
                # new transaction
                if trans is not None:
                    yield trans
                date = row[CSVReader.Headers.DATE.value]
                date = datetime.datetime.strptime(date, '%m/%d/%Y')
                description = row[CSVReader.Headers.DESC.value]
                commodity = row[CSVReader.Headers.COMMODITY.value]
                trans = transaction.RawTransaction(
                        date=date,
                        description=description,
                        commodity=commodity)
            # add current split
            account = row[CSVReader.Headers.ACCOUNT.value]
            memo = row[CSVReader.Headers.MEMO.value]
            value = row[CSVReader.Headers.VALUE.value]
            amount = row[CSVReader.Headers.AMOUNT.value]
            split = transaction.RawSplit(account, memo, value, amount)
            trans.append_split(split)

        if trans is not None:
            yield trans

    def __next__(self):
        row = next(self.reader)
        return row
