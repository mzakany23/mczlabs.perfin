import datetime
import os

from perfin import get_transactions

TEST_FILE_DIR = "{}/files".format(os.path.dirname(os.path.abspath(__name__)))

"""
    how to run

    make test TEST_FILE=test_transactions
"""


def test_basic_schema_capone(csv_finder):
    """
        how to run

        make test TEST_FILE=test_transactions TEST_FN=test_basic_schema_capone
    """
    finder = csv_finder("capone_test_basic")

    for t in get_transactions(finder):
        doc = t.doc
        t.account_name == "capital_one"
        assert doc["account_name"] == "capital_one"
        assert doc
        assert isinstance(doc["date"], datetime.datetime)
        assert t.amount < 0


def test_basic_schema_53(csv_finder):
    """
        how to run

        make test TEST_FILE=test_transactions TEST_FN=test_basic_schema
    """
    finder = csv_finder("fifththird_test_basic")

    for t in get_transactions(finder):
        doc = t.doc
        t.account_name == "fifth_third"
        assert doc["account_name"] == "fifth_third"
        assert doc
        assert isinstance(doc["date"], datetime.datetime)
        assert t.amount < 0


def test_basic_schema_chase(csv_finder):
    """
        how to run

        make test TEST_FILE=test_transactions TEST_FN=test_basic_schema_chase
    """
    finder = csv_finder("chase_test_invert")

    for t in get_transactions(finder):
        doc = t.doc
        assert doc
        assert isinstance(doc["date"], datetime.datetime)
        assert t.amount < 0


def test_get_transactions(finder):
    """
        how to run

        make test TEST_FILE=test_transactions TEST_FN=test_get_transactions
    """

    for t in get_transactions(finder):
        doc = t.doc

        try:
            assert isinstance(doc["amount"], float)
            assert isinstance(doc["description"], str)
            assert isinstance(doc["date"], datetime.datetime)
            assert isinstance(doc["category"], str) or doc["category"] is None
            assert isinstance(doc["account_name"], str)
        except (AssertionError, KeyError) as e:
            raise Exception(f"{t.account_name}, {doc}") from e
