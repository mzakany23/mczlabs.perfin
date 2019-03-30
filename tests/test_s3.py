import pytest
from perfin.handler import *

'''
    HOW_TO_RUN_TESTS
        make sure python tls is 1.2 compatable
        make sure pytest is installed
        (with warnings)
        pytest ./tests/test_files.py
        (without warnings)
        pytest -q ./tests/test_s3.py -p no:warnings
'''

# -------------------------------------------------------------------
# LEGEND
# -------------------------------------------------------------------

'''
    0. test helpers
    1. fixtures
    2. unit tests (no db required)
    3. integration tests (elasticsearch required)
'''

# -------------------------------------------------------------------
# 0. test helpers
# -------------------------------------------------------------------

def insert_fn(*args, **kwargs):
    return True


def read_csv_fn(*args, **kwargs):
    yield {
        'document' : {

        },
        '_group' : 'foo',
        '_id' : 'foo'
    }


# -------------------------------------------------------------------
# 1. fixtures
# -------------------------------------------------------------------


@pytest.fixture
def event():
    return {
      'Records': [
        {
          's3': {
            's3SchemaVersion': '1.0',
            'configurationId': '07cdd4c6-53ea-41d1-9536-e64d6661708d',
            'bucket': {
              'name': 'mzakany-perfin',
              'ownerIdentity': {
                'principalId': 'A1KXLJ5C0RVBLI'
              },
              'arn': 'arn:aws:s3:::mzakany-perfin'
            },
            'object': {
              'key' : '2018-10-10_transaction_download_5.csv',
              'size': 2577,
              'eTag': '47eb72587b90a88cf07820543e938d11',
              'sequencer': '005BB006BB55D4F51F'
            }
          }
        }
      ]
    }


@pytest.fixture 
def context():
    return {}

  
# -------------------------------------------------------------------
# 2. unit tests (es access stubbed)
# -------------------------------------------------------------------


def test_insert_file(event, context):
    files = process_files(
        event, 
        context, 
        insert_fn=insert_fn,
        read_csv_fn=read_csv_fn
    )
    assert files is None
    

# -------------------------------------------------------------------
# 3. integration tests (requires elasticsearch)
# -------------------------------------------------------------------
