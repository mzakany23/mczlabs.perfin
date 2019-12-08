import os
import pytest
from .utils.helpers import *
from assertpy import assert_that
from ..lib.file_matching.config import *
from ..lib.file_matching.analyzer import *
from ..lib.file_matching.matching import *
from ..lib.file_matching.mapping import *
from ..lib.file_matching.policy import *
from perfin.lib.file_matching.util.support import *


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

    return BASE_POLICY
        

@pytest.fixture
def file_analyzer_scenarios():
    '''match a file against the policy as a whole'''
    test_file_dir = '{}/files'.format(os.path.dirname(os.path.abspath(__file__)))

    return [
        {
            'assertion' : 'is_equal_to',
            'should_be' : 'CAPITAL_ONE',
            'filename' : '{}/2019-03-14_transaction_download.csv'.format(test_file_dir), 
        },
        {
            'assertion' : 'is_equal_to',
            'should_be' : 'FIFTH_THIRD',
            'filename' : '{}/53_03_07_09.CSV'.format(test_file_dir), 
        },
        {
            'assertion' : 'is_equal_to',
            'should_be' : 'FIFTH_THIRD',
            'filename' : '{}/EXPORT3_14_2019.CSV'.format(test_file_dir), 
        },
        {
            'assertion' : 'is_equal_to',
            'should_be' : 'CHASE',
            'filename' : '{}/Chase3507_Activity20190314.CSV'.format(test_file_dir), 
        },
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
            'assertion' : 'is_equal_to',
            'should_be' : 'CAPITAL_ONE',
            'header' : [ ' Category', ' Debit', ' Credit'],
            'filename' : 'mzakany-perfin/capitalone3507_Activity20190314.CSV'
        }
        
    ]


# -------------------------------------------------------------------
# 2. unit tests (es access stubbed)
# -------------------------------------------------------------------


def test_file_analyzer(policy, file_analyzer_scenarios):
    for scenario in file_analyzer_scenarios:
        assertion = scenario['assertion']
        should_be = scenario['should_be']

        params = {
            'policy' : policy,
            'filename' : scenario['filename'],
        }

        if 'header' in scenario:
            params['header'] = scenario['header']
        else:
            with open(scenario['filename']) as f:
                params['header'] = f.readline().strip().split(',')

        analyzer = FileAnalyzer(**params)

        assert_helper(assertion, analyzer.top_match.domain, should_be)
