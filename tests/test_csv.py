import datetime
import os
from pathlib import Path

from perfin import get_file_names, get_transactions
from perfin.csv import Row
from perfin.settings import config

TEST_FILE_DIR = "{}/files".format(os.path.dirname(os.path.abspath(__name__)))

"""
    how to run

    make test TEST_FILE=test_csv
"""


def test_get_file_names(mocker, finder):
    """
        how to run

        make test TEST_FILE=test_csv TEST_FN=test_get_file_names
    """
    for old_file, new_file_name in get_file_names(finder):
        parts = new_file_name.split("____")
        fd, td = parts[1].split("--")
        fd = datetime.datetime.strptime(fd, config.date_fmt)

        assert len(parts) == 3
        assert isinstance(fd, datetime.datetime)
        assert isinstance(old_file, Path)
        assert isinstance(new_file_name, str)


def test_get_transactions(finder):
    """
        how to run

        make test TEST_FILE=test_csv TEST_FN=test_get_transactions
    """
    for t in get_transactions(finder):
        doc = t.doc

        try:
            assert isinstance(doc["amount"], float)
            assert isinstance(doc["description"], str)
            assert isinstance(doc["date"], datetime.datetime)
            assert isinstance(doc["category"], str) or doc["category"] is None
            assert isinstance(doc["account_name"], str)
        except Exception as e:
            raise Exception(f"{doc}, {str(e)}")


def test_csv_key():
    """
        how to run

        make test TEST_FILE=test_csv TEST_FN=test_csv_key
    """

    row = Row(None, None, {})
    assert row._make_key("45540 VERTICAL K DIR DEP 66 011521") == "VERTICALKD"
    assert row._make_key("HEROKU JUL-39703527") == "HEROKUJUL"
    assert row._make_key("Prime Video*3H5G70UV3") == "PRIMEVIDEO"
    assert row._make_key("TST* ON THE RISE ARTISAN") == "TSTONTHER"
    assert row._make_key("APPLE.COM/BILL",) == "APPLECOM"
    assert row._make_key("PHO &amp; RICE") == "PHOAMPRI"
