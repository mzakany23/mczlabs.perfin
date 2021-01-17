import datetime
import os
from pathlib import Path

from perfin import get_file_names, get_transactions
from perfin.settings import config

TEST_FILE_DIR = "{}/files".format(os.path.dirname(os.path.abspath(__name__)))

"""
    how to run

    make test TEST_FILE=test_munging
"""


def test_get_file_names(mocker, file_dir):
    """
        how to run

        make test TEST_FILE=test_munging TEST_FN=test_get_file_names
    """
    for old_file, new_file_name in get_file_names(file_dir):
        parts = new_file_name.split("____")
        fd, td = parts[1].split("--")
        fd = datetime.datetime.strptime(fd, config.date_fmt)

        assert len(parts) == 3
        assert isinstance(fd, datetime.datetime)
        assert isinstance(old_file, Path)
        assert isinstance(new_file_name, str)


def test_get_transactions(file_dir):
    """
        how to run

        make test TEST_FILE=test_munging TEST_FN=test_get_transactions
    """
    for t in get_transactions(file_dir):
        doc = t.doc
        assert isinstance(doc["amount"], float)
        assert isinstance(doc["description"], str)
        assert isinstance(doc["date"], str)
        assert isinstance(doc["category"], str)
        assert isinstance(doc["account"], str)
