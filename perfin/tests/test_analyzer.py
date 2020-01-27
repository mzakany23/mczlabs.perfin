import os
import pytest
from ..lib.file_matching.config import TRIM_FIELD
from ..lib.file_matching.analyzer import FileAnalyzer


'''
    HOW_TO_RUN_TESTS
        make sure python tls is 1.2 compatable
        make sure pytest is installed
        (with warnings)
        pytest ./perfin/tests/test_analyzer.py -k 'test_random_filetype'  -p no:warnings
        (without warnings)
        pytest -q ./tests/test_files.py -p no:warnings
'''

# -------------------------------------------------------------------
# LEGEND
# -------------------------------------------------------------------

'''
    1. fixtures
    2. unit tests (no db required)
'''


# -------------------------------------------------------------------
# 1. fixtures
# -------------------------------------------------------------------

DIR = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture
def dummy_row():
    return {
      '_id': '3a34633eb9b64eaae92c5324f849b2caf9e5859dea6c24fce619110088efa24e',
      'document': {
        'account': 'CHASE',
        'post date': '2019-03-13',
        'description': 'CLEV HTS - PARKING',
        'category': 'Travel',
        'type': 'Sale',
        'amount': -0.75
      },
      '_group': 'CLEV HTS -'
    }


@pytest.fixture
def chase_file():
    return f'{DIR}/files/chase____2019.01.12.csv'


@pytest.fixture
def fifth_third_file():
    return f'{DIR}/files/fifth_third____2019.01.12.csv'


@pytest.fixture
def no_account_file():
    return f'{DIR}/files/EXPORTS.csv'

# -------------------------------------------------------------------
# 2. unit tests (es access stubbed)
# -------------------------------------------------------------------

def test_account_name(chase_file):
    analyzer = FileAnalyzer(chase_file, s3=False)
    assert analyzer.account_name == 'CHASE'


def test_chase_file(chase_file, dummy_row):
    analyzer = FileAnalyzer(chase_file, s3=False, group_by='description')
    for row in analyzer.get_rows():
        document = row['document']
        assert list(document.keys()) == [
            'account',
            'date',
            'description',
            'category',
            'type',
            'amount'
        ]
        assert '_group' in row
        assert row['document']['date'] == '2019-03-13'
        return


def test_fifth_third_file(fifth_third_file):
    analyzer = FileAnalyzer(file_path=fifth_third_file, s3=False)
    assert analyzer.account_name == 'FIFTH_THIRD'
    assert analyzer.schema == {'date': 0, 'description': 1, 'amount': 2}


def test_no_account(no_account_file):
    try:
        analyzer = FileAnalyzer(file_path=no_account_file, s3=False)
    except Exception as e:
        assert str(e) == 'Account name EXPORTS.csv is invalid.'


def test_globals():
    assert TRIM_FIELD
