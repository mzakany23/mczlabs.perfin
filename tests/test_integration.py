import pytest
from .utils.helpers import *
from assertpy import assert_that
from perfin.lib.file_matching.config import *
from perfin.lib.file_matching.analyzer import *
from perfin.lib.file_matching.matching import *
from perfin.lib.file_matching.mapping import *
from perfin.lib.file_matching.policy import *
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
    2. integration tests (elasticsearch required)
'''


# -------------------------------------------------------------------
# 1. fixtures
# -------------------------------------------------------------------


# -------------------------------------------------------------------
# 2. unit tests (es access stubbed)
# -------------------------------------------------------------------


# -------------------------------------------------------------------
# 2. integration tests (requires elasticsearch)
# -------------------------------------------------------------------


def test_integration():
    '''
        DESCRIPTION 
            To show how works
        EXAMPLE:
            Just run tests
    '''
    assert 1==1

