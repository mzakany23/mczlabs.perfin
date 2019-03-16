import pytest
import re
from fuzzywuzzy import fuzz
import operator


def setupdjango():
    import django
    import os
    os.environ['DJANGO_SETTINGS_MODULE'] = 'athena_project.settings.dev'
    django.setup()

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
def base_tests():
    '''
        TITLE
            Test learning about the file
        DESCRIPTION
            Trying to test being able to know what file we are talking about.
            This needs to very robust if don't know what file then can't parse!
    '''

    return {
        'policy' : {
            # chase
            "['Type', 'Trans Date', 'Post Date', 'Description', 'Amount']" : {
                "name" : "CHASE",
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
            "['Date', 'Description', 'Check Number', 'Amount']" : {
                "name" : "FIFTH_THIRD",
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
            "[' Transaction Date', ' Posted Date', ' Card No.', ' Description', ' Category', ' Debit', ' Credit']" : {
                "name" : "CAPITAL_ONE",
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
        },
        'data' : [
            {
                'should_be' : 'CHASE',
                # header from file
                'header' : ['Type','TransDate','PostDate','Description','Amount'],
                # this is also given in file
                'file_name' : 'mzakany-perfin/Chase3507_Activity20190314.CSV'
            }
        ]
    }


  
# -------------------------------------------------------------------
# 2. unit tests (es access stubbed)
# -------------------------------------------------------------------


class FileScore(object):
    matches = []
    
    def update(self, domain, policy_header, header, file_name):
        try:
            header = '%s' % header
            self.matches.append({
                'domain' : domain,
                'header_score' : fuzz.ratio(policy_header, header),
                'filename_score' : fuzz.ratio(domain, file_name),
            })
        except:
            self.not_in_index.append(1)


class FileType(object):

    def __init__(self, *args, **kwargs):
        self.policy = kwargs.get('policy', [])
        self.header = kwargs.get('header', [])
        self.file_name = kwargs.get('file_name', [])
    
    @property
    def score(self):
        return self.calculate_file_score()
    
    @property
    def top_match(self):
        return self.score[0]

    def calculate_file_score(self):
        score = FileScore()
        for policy_header, policy_key in self.policy.items():
            score.update(policy_key['name'], policy_header, self.header, self.file_name)
        
        first_sort = sorted(score.matches, key=operator.itemgetter('header_score'), reverse=True)
        return sorted(first_sort, key=operator.itemgetter('filename_score'), reverse=True)
        

def test_unit(base_tests):
    '''run tests'''
    policy = base_tests['policy']
    data_item = base_tests['data'][0]

    file_type = FileType(
        policy=policy,
        file_name=data_item['file_name'],
        header=data_item['header'],
    )
    
    assert file_type.top_match['domain'] == data_item['should_be']
    

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
