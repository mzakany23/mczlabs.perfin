import pytest
from perfin.util.classes import *
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
def scenarios():
    return [
        {
            'should_be' : 'CHASE',
            # header from file
            'header' : ['Type','TransDate','PostDate','Description','Amount'],
            # this is also given in file
            'filename' : 'mzakany-perfin/Chase3507_Activity20190314.CSV'
        }
    ]


@pytest.fixture
def file_match_scenarios():
    return [
        {
            'domain' : 'CHASE',
            'should_be' : '>= 198',
            'filename' : 'mzakany-perfin/Chase3507_Activity20190314.CSV',
            'policy_header' : ['Type', 'Trans Date', 'Post Date', 'Description', 'Amount'],
            'header' : ['Type','TransDate','PostDate','Description','Amount'],
        },
        {
            'domain' : 'CHASE',
            'should_be' : '<= 227',
            'filename' : 'mzakany-perfin/CapitalOne3507_Activity20190314.CSV',
            'policy_header' : ['Post Date', 'Description', 'Amount'],
            'header' : ['Type','TransDate','PostDate','Description','Amount'],
        },
        {
            'domain' : 'CHASE',
            'should_be' : '< 50',
            'filename' : 'mzakany-perfin/FifthThird3507_Activity20190314.CSV',
            'policy_header' : ['Post Date', 'Description', 'Amount'],
            'header' : ['Type','TransDate','PostDate','Description','Amount'],
        },
        {
            'domain' : 'CHASE',
            'should_be' : '> 150',
            'filename' : 'mzakany-perfin/chase_financial.CSV',
            'policy_header' : ['Type', 'Trans Date', 'Post Date', 'Description', 'Amount'],
            'header' : ['Type','Trans Date','Post Date','Description','Amount'],
        }
    ]
  

@pytest.fixture 
def mappings():
    return [
        {
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


def test_mappings(mappings):
    for mapping in mappings:
        mapping = Mapping(fields=mapping['header'], boost=mapping['boost'])
        import pdb; pdb.set_trace()
        

# def test_file_analyzer(policy, scenarios):
#     '''run tests'''
    
#     for scenario in scenarios:
#         file_type = FileAnalyzer(
#             policy=policy,
#             filename=scenario['filename'],
#             header=scenario['header'],
#         )

#         assert file_type.top_match.domain == scenario['should_be']
    

# def test_file_match(file_match_scenarios):
#     for scenario in file_match_scenarios:
#         domain = scenario['domain']
#         filename = scenario['filename']
#         policy_header = scenario['policy_header']
#         header = scenario['header']
#         headers = [policy_header, header]
#         should_be = scenario['should_be']
#         equality, unit = should_be.split(' ')
#         unit = int(unit)

#         match = FileMatch(
#             domain=domain,
#             filename=filename,
#             headers=headers,
#         )

#         if equality == '>':
#             assert match.total_score > unit
#         elif equality == '>=':
#             assert match.total_score >= unit
#         elif equality == '<':
#             assert match.total_score < unit
#         elif equality == '<=':
#             assert match.total_score <= unit
#         else:
#             assert match.total_score == unit



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
