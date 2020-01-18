import pytest
from perfin.lib.file_matching.util.support import get_account_lookup


'''
    HOW_TO_RUN_TESTS
        pytest ./perfin/tests/test_plaid.py -p no:warnings

'''

@pytest.fixture
def res():
    return {
      'accounts': [
        {
          'account_id': 'xqoeX8YOEasqxwN3zDMQtBypDXw5e6CMbxo6e',
          'balances': {
            'available': 61518,
            'current': 61518,
            'iso_currency_code': 'USD',
            'limit': None,
            'unofficial_currency_code': None
          },
          'mask': '7080',
          'name': '5/3 ESSENTIAL CHECKING',
          'official_name': '5/3 ESSENTIAL CHECKING',
          'subtype': 'checking',
          'type': 'depository'
        }
      ],
      'item': {
        'available_products': [
          'auth',
          'balance'
        ],
        'billed_products': [
          'transactions'
        ],
        'consent_expiration_time': None,
        'error': None,
        'institution_id': 'ins_26',
        'item_id': 'dZ7ea6KDjbSDQZJEbxK4H3nwQnBDDDUb593zQ',
        'webhook': ''
      },
      'request_id': 'HXCkHRvhH3hF57x',
      'total_transactions': 31,
      'transactions': [
        {
          'account_id': 'xqoeX8YOEasqxwN3zDMQtBypDXw5e6CMbxo6e',
          'account_owner': None,
          'amount': -2087.39,
          'authorized_date': None,
          'category': [
            'Transfer',
            'Payroll'
          ],
          'category_id': '21009000',
          'date': '2020-01-17',
          'iso_currency_code': 'USD',
          'location': {
            'address': None,
            'city': None,
            'lat': None,
            'lon': None,
            'state': None,
            'store_number': None,
            'zip': None
          },
          'name': 'MUSICAL ARTS ASS Payroll XXXXXXXXXXX1761 011720',
          'payment_channel': 'other',
          'payment_meta': {
            'by_order_of': None,
            'payee': None,
            'payer': None,
            'payment_method': None,
            'payment_processor': None,
            'ppd_id': None,
            'reason': None,
            'reference_number': None
          },
          'pending': False,
          'pending_transaction_id': 'pQ3epvZAVKC6QYPwX4Mgtj1XDq8ywJCJxPmMA',
          'transaction_id': '6A8kDngR7MSje9NwZO3Xi9L4RwRXnrTaXJ9wm',
          'transaction_type': 'special',
          'unofficial_currency_code': None
        }
      ]
    }


def test_account_lookup(res):
    lookup = get_account_lookup(res['accounts'])
    assert lookup['xqoeX8YOEasqxwN3zDMQtBypDXw5e6CMbxo6e']['subtype'] == 'checking'
