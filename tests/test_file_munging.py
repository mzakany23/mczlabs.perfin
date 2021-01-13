import os
from pathlib import Path

from perfin import get_file_names, get_transactions

TEST_FILE_DIR = "{}/files".format(os.path.dirname(os.path.abspath(__name__)))

"""
    how to run

    make test TEST_FILE=test_file_munging
"""


def test_get_file_names(mocker):
    """
        how to run

        make test TEST_FILE=test_file_munging TEST_FN=test_get_file_names
    """
    for old_file, new_file in get_file_names():
        assert isinstance(old_file, Path)
        assert isinstance(new_file, Path)


def test_get_transactions():
    """
        how to run

        make test TEST_FILE=test_file_munging TEST_FN=test_get_transactions
    """
    for trans in get_transactions():
        pass
