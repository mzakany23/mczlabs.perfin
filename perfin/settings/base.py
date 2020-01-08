import os
import json

CLIENT_ID = os.environ.get('CLIENT_ID')
SECRET = os.environ.get('SECRET')
PUBLIC_KEY = os.environ.get('PUBLIC_KEY')
PLAID_ENV = os.environ.get('PLAID_ENV')

try:
	ACCOUNT_LOOKUP = json.loads(os.environ.get('ACCOUNT_LOOKUP'))
except:
	ACCOUNT_LOOKUP = None

from .dev import *