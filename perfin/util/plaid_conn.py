from plaid import Client

from ..settings.base import load_settings


settings = load_settings()

CLIENT_ID, SECRET, PUBLIC_KEY, PLAID_ENV = (
    settings['CLIENT_ID'],
    settings['SECRET'],
    settings['PUBLIC_KEY'],
    settings['PLAID_ENV']
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
