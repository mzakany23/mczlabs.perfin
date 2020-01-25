from perfin.util.dynamodb_conn import get_user_accounts

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


def get_transactions(client, plaid_account, start_date, end_date):
    token = plaid_account.token

    res = client.Transactions.get(
        plaid_account.token,
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