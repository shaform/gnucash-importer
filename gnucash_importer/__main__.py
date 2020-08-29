import argparse

import gnucash

from . import reader


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('gnucash_path')
    parser.add_argument('csv_path')
    return parser.parse_args()


def main():
    args = parse_args()

    txns = []
    with open(args.csv_path, newline='') as infile:
        txn_reader = reader.CSVReader(infile)
        for txn in txn_reader:
            txns.append(txn)
    print('%d transactions loaded...' % len(txns))

    txns = [txn for txn in txns if txn.validate()]
    print('%d valid transactions...' % len(txns))

    print('Opening GnuCash file...')
    with gnucash.Session(
            args.gnucash_path,
            gnucash.SessionOpenMode.SESSION_NORMAL_OPEN) as session:
        book = session.book
        print('Start inserting transactions...')
        for txn in txns:
            txn.create_transaction(book)
    print('Done!')


if __name__ == '__main__':
    main()
