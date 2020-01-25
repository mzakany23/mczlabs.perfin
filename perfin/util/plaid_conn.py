from perfin.util.dynamodb_conn import get_accounts

from plaid import Client

from ..settings.base import (
    CLIENT_ID,
    PLAID_ENV,
    PUBLIC_KEY,
    SECRET
)


def get_client():
    return Client(
        client_id=CLIENT_ID,
        secret=SECRET,
        public_key=PUBLIC_KEY,
        environment=PLAID_ENV
    )


def get_transactions(client, account_type, start_date, end_date):
    account = [account for account in get_accounts(account_type)][0]
    token = account.token
    
    res = client.Transactions.get(
        account.token,
        start_date,
        end_date,
    )

    yield res

    total = res['total_transactions']
    trans = res['transactions']

    current = 0

    current += len(trans)

    while current < total:
        res = client.Transactions.get(token, start_date, end_date, offset=current)

        current += len(res['transactions'])

        yield res
