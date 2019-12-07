import pytest
import os
from .utils.helpers import *
from assertpy import assert_that
from ..util.es import get_es_connection
from ..handler import insert_files

'''
    HOW_TO_RUN_TESTS
        make sure python tls is 1.2 compatable
        make sure pytest is installed
        (with warnings)
        pytest ./tests/test_files.py
        (without warnings)
        pytest -q ./tests/test_files.py -p no:warnings
'''

# -------------------------------------------------------------------
# LEGEND
# -------------------------------------------------------------------


'''
    1. fixtures
    2. integration tests (elasticsearch required)
'''


# -------------------------------------------------------------------
# 1. fixtures
# -------------------------------------------------------------------

@pytest.fixture
def file_paths():
    _dir = os.path.dirname(os.path.abspath(__file__))
    rows = ['{}/{}'.format(_dir, path) for path in os.listdir(_dir) if path.lower().endswith('.csv')]
    return rows

# -------------------------------------------------------------------
# 2. unit tests (es access stubbed)
# -------------------------------------------------------------------


# -------------------------------------------------------------------
# 2. integration tests (requires elasticsearch)
# -------------------------------------------------------------------


@pytest.mark.skipif(not os.environ.get('RUN_INTEGRATION_TESTS'), reason="Does not have local elasticsearch running")
def test_integration(file_paths):
    ES_CONN = get_es_connection()

    '''
        DESCRIPTION 
            To show how works
        EXAMPLE:
            Just run tests
    '''
    insert_files(ES_CONN, file_paths, 'transactions_write', read_from_s3=False)
