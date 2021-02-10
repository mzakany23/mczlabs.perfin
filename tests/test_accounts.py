import os

from perfin.accounts import find_account, get_file_columns

TEST_FILE_DIR = "{}/files".format(os.path.dirname(os.path.abspath(__name__)))

"""
    how to run

    make test TEST_FILE=test_accounts
"""


def test_get_file_columns(df_finder):
    """
        how to run

        make test TEST_FILE=test_accounts TEST_FN=test_get_file_columns
    """
    account = find_account("capital_one")
    df = df_finder("capone_test_basic")
    file_columns, sort_key = get_file_columns(df, account)

    assert sort_key["key"] == "transaction_posted_date"
    assert len(file_columns) == 3
