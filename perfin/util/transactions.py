from plaid import Client
from ..settings.base import (
	CLIENT_ID, 
	SECRET, 
	PUBLIC_KEY, 
	PLAID_ENV, 
	ACCOUNT_LOOKUP
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
    return client.Transactions.get(item['token'], start_date, end_date)