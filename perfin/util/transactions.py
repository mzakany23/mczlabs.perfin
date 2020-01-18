from plaid import Client

from ..settings.base import (
    ACCOUNT_LOOKUP,
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
    if account_type not in ACCOUNT_LOOKUP:
        return
    item = ACCOUNT_LOOKUP[account_type]

    res = client.Transactions.get(
        item['token'],
        start_date,
        end_date,
    )
    import pdb; pdb.set_trace()
    yield res

    total = res['total_transactions']
    trans = res['transactions']

    current = 0

    current += len(trans)
    
    while current < total:
        res = client.Transactions.get(item['token'],start_date,end_date,offset=current)

        current += len(res['transactions'])
        
        yield res
