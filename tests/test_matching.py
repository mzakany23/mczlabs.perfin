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
def file_match_scenarios():
    '''match a file against a single policy'''

    return [
        {
            'domain' : 'CHASE',
            'assertion' : 'is_greater_than_or_equal_to',
            'should_be' : 198,
            'filename' : 'mzakany-perfin/Chase3507_Activity20190314.CSV',
            'policy_header' : ['Type', 'Trans Date', 'Post Date', 'Description', 'Amount'],
            'header' : ['Type','TransDate','PostDate','Description','Amount'],
        },
        {
            'domain' : 'CHASE',
            'assertion' : 'is_less_than_or_equal_to',
            'should_be' : 227,
            'filename' : 'mzakany-perfin/CapitalOne3507_Activity20190314.CSV',
            'policy_header' : ['Post Date', 'Description', 'Amount'],
            'header' : ['Type','TransDate','PostDate','Description','Amount'],
        },
        {
            'domain' : 'CHASE',
            'assertion' : 'is_less_than',
            'should_be' : 50,
            'filename' : 'mzakany-perfin/FifthThird3507_Activity20190314.CSV',
            'policy_header' : ['Post Date', 'Description', 'Amount'],
            'header' : ['Type','TransDate','PostDate','Description','Amount'],
        },
        {
            'domain' : 'CHASE',
            'assertion' : 'is_greater_than',
            'should_be' : 150,
            'filename' : 'mzakany-perfin/chase_financial.CSV',
            'policy_header' : ['Type', 'Trans Date', 'Post Date', 'Description', 'Amount'],
            'header' : ['Type','Trans Date','Post Date','Description','Amount'],
        },
        {
            'domain' : 'CHASE',
            'assertion' : 'is_not_equal_to',
            'should_be' : 'CHASE',
            'policy_header' : ['Type','TransDate','PostDate','Description','Amount'],
            'header' : ['Type','Trans Date','Post Date','Description','Amount'],
            'filename' : 'mzakany-perfin/fifth_third3507_Activity20190314.CSV'
        }
    ]
  

# -------------------------------------------------------------------
# 2. unit tests (es access stubbed)
# -------------------------------------------------------------------

    
def test_file_match(file_match_scenarios):
    for scenario in file_match_scenarios:
        domain = scenario['domain']
        filename = scenario['filename']
        policy_header = scenario['policy_header']
        header = scenario['header']
        headers = [policy_header, header]

        assertion = scenario['assertion']
        should_be = scenario['should_be']
        
        policy_body = BASE_POLICY[domain]

        policy = FilePolicy(
            domain=domain,
            policy_body=policy_body
        )

        match = FileMatch(
            policy=policy,
            header=header,
            filename=filename
        )
        
        assert_helper(assertion, match.total_score, should_be)
        