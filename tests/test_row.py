import pytest
from ..lib.file_matching.policy import *
from ..lib.file_matching.config import *

'''
    HOW_TO_RUN_TESTS
        make sure python tls is 1.2 compatable
        make sure pytest is installed
        (with warnings)
        pytest ./tests
        (without warnings)
        pytest -q ./tests -p no:warnings
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




# -------------------------------------------------------------------
# 1. fixtures
# -------------------------------------------------------------------


@pytest.fixture
def mapping_params():
    return {
        'header' : [' Transaction Date', ' Posted Date', ' Card No.', ' Description', ' Category', ' Debit', ' Credit'],
        'columns' : {
            "date" : 1,
            "card" : 2,
            "description" : 3,
            "category" : 4,
            "amount" : 5,
            "credit" : 6,
        }     
    }


@pytest.fixture
def scenarios():
    return [
        ['2018-10-08', '2018-10-09', '3457', 'HEROKU SEP-20833205', 'Internet', '14.00', '']
    ]


# -------------------------------------------------------------------
# 2. unit tests (es access stubbed)
# -------------------------------------------------------------------


def test_unit(mapping_params, scenarios):
    mapping = Mapping(
        header=mapping_params['header'], 
        columns=mapping_params['columns']
    )
    
    assert mapping.success


# -------------------------------------------------------------------
# 3. integration tests (requires elasticsearch)
# -------------------------------------------------------------------


