import datetime

from perfin.lib.models import PerfinAccount


def create_table():
    PerfinAccount.create_table(wait=True)


def user_accounts(username):
    query = PerfinAccount.username == username
    for account in PerfinAccount.scan(filter_condition=query, index_name='username-index'):
        yield account


def get_user_accounts(username, account_name=None):
    user_query = PerfinAccount.username == username

    if account_name:
    	query = user_query & (PerfinAccount.account_name == account_name)
    else:
    	query = user_query

    for account in PerfinAccount.scan(filter_condition=query):
        yield account
