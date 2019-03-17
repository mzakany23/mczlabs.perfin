import pytest
from assertpy import assert_that
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
    3. integration tests (elasticsearch required)
'''

# -------------------------------------------------------------------
# 0. test helpers
# -------------------------------------------------------------------


def assert_helper(assertion, item, should_be):
    getattr(assert_that(item), assertion)(should_be)


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

    return {
        
        # chase
        "CHASE" : {
            "header" : ['Type', 'Trans Date', 'Post Date', 'Description', 'Amount'],
            "trim" : {
                "field" : "description",
                "value" : 10
            }, 
            "fields" : {
                "date" : 2,
                "description" : 3,
                "amount" : 4
            }
        },
        # Fifth third
        "FIFTH_THIRD" : {
            "header" : ['Date', 'Description', 'Check Number', 'Amount'],
            "trim" : {
                "field" : "description",
                "value" : 10
            }, 
            "fields" : {
                "date" : 0,
                "description" : 1,
                "check_num" : 2,
                "amount" : 3
            }   
        },
        # Capital one
        "CAPITAL_ONE" : {
            "header" : [' Transaction Date', ' Posted Date', ' Card No.', ' Description', ' Category', ' Debit', ' Credit'],
            "trim" : {
                "field" : "description",
                "value" : 10
            }, 
            "fields" : {
                "date" : 1,
                "card" : 2,
                "description" : 3,
                "category" : 4,
                "amount" : 5,
                "credit" : 6,
            }     
        }
    }
        

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
        }
    ]


@pytest.fixture
def file_match_scenarios():
    '''match a single file against a single policy'''
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
  

@pytest.fixture 
def mapping_scenarios():
    return [
        {
            'assertion' : 'is_equal_to',
            'should_be' : True,
            'header' : ['Type', 'Trans Date', 'Post Date', 'Description', 'Amount'],
            'boost' : {
                "date" : 2,
                "description" : 3,
                "amount" : 4
            }
        }
    ]


# -------------------------------------------------------------------
# 2. unit tests (es access stubbed)
# -------------------------------------------------------------------


# def test_mappings(mapping_scenarios):
#     for mapping in mapping_scenarios:
#         mapping_obj = Mapping(fields=mapping['header'], boost=mapping['boost'])
#         assertion = mapping['assertion']
#         should_be= mapping['should_be']
        
#         assert_helper(assertion, mapping_obj.matches_boost, should_be)


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

    
# def test_file_match(file_match_scenarios):
#     for scenario in file_match_scenarios:
#         domain = scenario['domain']
#         filename = scenario['filename']
#         policy_header = scenario['policy_header']
#         header = scenario['header']
#         headers = [policy_header, header]

#         assertion = scenario['assertion']
#         should_be = scenario['should_be']
    
#         match = FileMatch(
#             domain=domain,
#             filename=filename,
#             headers=headers,
#         )
        
#         assert_helper(assertion, match.total_score, should_be)
        


# -------------------------------------------------------------------
# 3. integration tests (requires elasticsearch)
# -------------------------------------------------------------------


# def test_integration(base_config):
#     '''
#         DESCRIPTION 
#             To show how works
#         EXAMPLE:
#             Just run tests
#     '''
#     assert base_config == 'foo'
