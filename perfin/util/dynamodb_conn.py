import datetime

from perfin.lib.models.account import PerfinAccount
from perfin.settings.dev import ACCOUNT_LOOKUP


def seed_account():
    for k, v in ACCOUNT_LOOKUP.items():
        account = PerfinAccount(
            v['item'],
            username='mzakany',
            account_name=k,
            first_name='mike',
            last_name='zakany',
            token=v['token'],
            last_updated=datetime.datetime.now()
        )

        account.save()


def create_table():
    PerfinAccount.create_table(wait=True)


def user_accounts(username):
    query = PerfinAccount.username == username
    for account in PerfinAccount.scan(filter_condition=query, index_name='username-index'):
        yield account


def get_accounts(account_name):
    query = PerfinAccount.account_name == account_name
    for account in PerfinAccount.scan(filter_condition=query):
        yield account
