import pytest
from .utils.helpers import *
from assertpy import assert_that
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
    1. fixtures
    2. unit tests (no db required)
'''


# -------------------------------------------------------------------
# 1. fixtures
# -------------------------------------------------------------------


@pytest.fixture
def policy():
    '''
        TITLE
            Test learning about the file
        DESCRIPTION
            Trying to test being able to know what file we are talking about.
            This needs to very robust if don't know what file then can't parse!
    '''

    return ACCOUNTS
        

@pytest.fixture
def file_analyizer_scenarios():
    '''match a file against the policy as a whole'''

    return [
        {
            'assertion' : 'is_equal_to',
            'should_be' : 'CHASE',
            'header' : ['Type','TransDate','PostDate','Description','Amount'],
            'filename' : 'mzakany-perfin/Chase3507_Activity20190314.CSV'
        },
        {
            'assertion' : 'is_not_equal_to',
            'should_be' : 'CHASE',
            'header' : ['Type','TransDate','PostDate','Description','Amount'],
            'filename' : 'mzakany-perfin/fifth_third3507_Activity20190314.CSV'
        },
        {
            'assertion' : 'is_equal_to',
            'should_be' : 'CAPITAL_ONE',
            'header' : [' Transaction Date', ' Posted Date', ' Card No.', ' Description', ' Category', ' Debit', ' Credit'],
            'filename' : 'mzakany-perfin/capitalone3507_Activity20190314.CSV'
        },
        {
            'assertion' : 'is_not_equal_to',
            'should_be' : 'CAPITAL_ONE',
            'header' : [ ' Category', ' Debit', ' Credit'],
            'filename' : 'mzakany-perfin/capitalone3507_Activity20190314.CSV'
        }
        
    ]


# -------------------------------------------------------------------
# 2. unit tests (es access stubbed)
# -------------------------------------------------------------------


def test_file_analyzer(policy, file_analyizer_scenarios):
    for scenario in file_analyizer_scenarios:
        assertion = scenario['assertion']
        should_be = scenario['should_be']

        analyzer = FileAnalyzer(
            policy=policy,
            filename=scenario['filename'],
            header=scenario['header'],
        )

        assert_helper(assertion, analyzer.top_match.domain, should_be)

