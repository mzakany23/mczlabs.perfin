from perfin.lib.models import PerfinAccount


def create_table():
    PerfinAccount.create_table(wait=True)


def user_accounts(username):
    query = PerfinAccount.username == username
    for account in PerfinAccount.scan(filter_condition=query, index_name='username-index'):
        yield account


def get_user_accounts(username, account_name=None, **kwargs):
    exclude_list = kwargs.get('exclude')
    user_query = PerfinAccount.username == username

    if account_name:
        query = user_query & (PerfinAccount.account_name == account_name)
    else:
        query = user_query

    for account in PerfinAccount.scan(filter_condition=query):
        if exclude_list and isinstance(exclude_list, list):
            account_name = account.account_name
            exclude = False
            for key in exclude_list:
                if key in account_name:
                    exclude = True
                    break
            if exclude:
                continue

        yield account
