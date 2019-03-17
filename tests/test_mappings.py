import pytest
from .utils.helpers import *
from perfin.lib.file_matching.config import *
from perfin.lib.file_matching.analyzer import *
from perfin.lib.file_matching.matching import *
from perfin.lib.file_matching.mapping import *
from perfin.lib.file_matching.policy import *

from perfin.util.support import *


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
    0. test helpers
    1. fixtures
    2. unit tests (no db required)
'''

# -------------------------------------------------------------------
# 0. test helpers
# -------------------------------------------------------------------



# -------------------------------------------------------------------
# 1. fixtures
# -------------------------------------------------------------------
  

@pytest.fixture 
def mapping_scenarios():
    '''test mapping boosting'''

    return [
        {
            'assertion' : 'is_equal_to',
            'should_be' : True,
            'header' : ['Type', 'Trans Date', 'Post Date', 'Description', 'Amount'],
            'columns' : {
                "date" : 2,
                "description" : 3,
                "amount" : 4
            }
        }
    ]


# -------------------------------------------------------------------
# 2. unit tests (es access stubbed)
# -------------------------------------------------------------------


def test_mappings(mapping_scenarios):
    for mapping in mapping_scenarios:
        mapping_obj = Mapping(
            fields=mapping['header'], 
            columns=mapping['columns']
        )
        assertion = mapping['assertion']
        should_be= mapping['should_be']
        
        assert_helper(assertion, mapping_obj.matches_columns, should_be)

