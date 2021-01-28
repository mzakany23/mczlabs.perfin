import os

from perfin.csv import Row

TEST_FILE_DIR = "{}/files".format(os.path.dirname(os.path.abspath(__name__)))

"""
    how to run

    make test TEST_FILE=test_csv
"""


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
