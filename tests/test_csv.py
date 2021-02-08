import os

from perfin.csv import _key

TEST_FILE_DIR = "{}/files".format(os.path.dirname(os.path.abspath(__name__)))

"""
    how to run

    make test TEST_FILE=test_csv
"""


def test_row(row_factory):
    """
        how to run

        make test TEST_FILE=test_csv TEST_FN=test_row
    """
    account_name = "somefakeaccount"
    account_type = "somefakeaccounttype"

    row = row_factory(account_name, account_type)

    assert row.account_name == account_name
    assert row.doc
    assert row.description


def test_csv_key():
    """
        how to run

        make test TEST_FILE=test_csv TEST_FN=test_csv_key
    """

    assert _key("45540 VERTICAL K DIR DEP 66 011521") == "VERTICALKD"
    assert _key("HEROKU JUL-39703527") == "HEROKUJUL"
    assert _key("Prime Video*3H5G70UV3") == "PRIMEVIDEO"
    assert _key("TST* ON THE RISE ARTISAN") == "TSTONTHER"
    assert _key("APPLE.COM/BILL",) == "APPLECOM"
    assert _key("PHO &amp; RICE") == "PHOAMPRI"
