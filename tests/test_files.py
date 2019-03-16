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
  
# -------------------------------------------------------------------
# 2. unit tests (es access stubbed)
# -------------------------------------------------------------------

class MalformedParams(Exception):
    pass


class Base(object):
    def __init__(self, *args, **kwargs):
        self.init_kwargs = kwargs 

    def validate(self, keys):
        kwargs = self.init_kwargs
        if isinstance(kwargs, dict):
            kwarg_keys = list(kwargs.keys())
            listed = [key for key in keys if kwargs.get(key)]
            if len(kwarg_keys) != len(listed):
                raise MalformedParams('{} {} {}'.format(self.__class__.__name__, kwarg_keys, listed))
            

class FilePolicyManager(Base):
    def __init__(self, *args, **kwargs):
        super(FilePolicyManager, self).__init__(*args, **kwargs)
        self.validate(['policy'])
        self.policy = kwargs.get('policy')
        self._policies = [FilePolicy(domain=k, policy_body=v) for k, v in self.policy.items()]

    @property
    def policies(self):
        return self._policies
        

class FilePolicy(Base):
    def __init__(self, *args, **kwargs):
        super(FilePolicy, self).__init__(*args, **kwargs)
        self.validate(['domain', 'policy_body'])
        self.domain = kwargs.get('domain')
        policy_body = kwargs.get('policy_body')
        self.policy_header = policy_body['header']

    @property
    def serialized_header(self):
        return '{}'.format(self.policy_header)
    

class FileMatchManager(Base):
    _matches = {}
    
    def add(self, file):
        total_score = sum([file.header_score, file.filename_score])
        self._matches[total_score] = file 

    @property
    def matches(self):
        return sorted(self._matches.items(), key=operator.itemgetter(0), reverse=True)
    
    @property
    def descending(self):
        return [item[1] for item in self.matches]


class FileMatch(Base):
    def __init__(self, *args, **kwargs):
        super(FileMatch, self).__init__(*args, **kwargs)
        self.validate(['domain', 'filename', 'headers'])
        
        self.domain = kwargs.get('domain')
        self.filename = kwargs.get('filename')
        self.headers = kwargs.get('headers')
        
        if self.headers and self.filename and self.domain:
            self.header_score = self.get_score(self.headers[0], self.headers[1])
            self.filename_score = self.get_score(self.domain, self.filename)
        
    def get_score(self, one, two):
        return fuzz.ratio(one, two)
        

class FileAnalyzer(Base):
    def __init__(self, *args, **kwargs):
        super(FileAnalyzer, self).__init__(*args, **kwargs)
        self.validate(['header', 'filename', 'policy'])

        policy = kwargs.get('policy')
        self.header = kwargs.get('header', [])
        self.filename = kwargs.get('filename', [])
        self.policy_manager = FilePolicyManager(policy=policy)

    @property
    def top_match(self):
        score = self.calculate_score() 
        return score[0] if len(score) > 0 else None

    @property
    def serialized_header(self):
        return '{}'.format(self.header)
    
    def calculate_score(self):
        matches = FileMatchManager()
        
        for policy in self.policy_manager.policies:
            file_match = FileMatch(
                domain=policy.domain,
                filename=self.filename,
                headers=[policy.serialized_header, self.serialized_header],
            )
            matches.add(file_match)
        return matches.descending

    
def test_unit(policy, scenarios):
    '''run tests'''
    
    for scenario in scenarios:
        file_type = FileAnalyzer(
            policy=policy,
            filename=scenario['filename'],
            header=scenario['header'],
        )

        assert file_type.top_match.domain == scenario['should_be']
    

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
