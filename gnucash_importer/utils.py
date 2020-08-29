def lookup_account(root_account, account_path):
    names = account_path.split(':')
    account = root_account
    for name in names:
        account = account.lookup_by_name(name)
    return account
