import pytest

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

    return [
        {
            'should_be' : 'chase',
            # header from file
            'header_key' : ['Transaction Date', 'Post Date', 'Description', 'Category', 'Type', 'Amount'],
            # key I make
            'account_types' : ['Type','TransDate','PostDate','Description','Amount'],
            # this is also given in file
            'file_name' : 'mzakany-perfin/Chase3507_Activity20190314.CSV'
        }
    ]


  
# -------------------------------------------------------------------
# 2. unit tests (es access stubbed)
# -------------------------------------------------------------------


def test_unit(base_tests):
    '''run tests'''
    for test in base_tests:
        header_key = test['header_key']
        account_types = test['account_types']
        file_name = test['file_name']
        should_be = test['should_be']

        assert should_be == 'chase'
    


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
