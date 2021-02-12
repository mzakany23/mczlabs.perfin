import os
from datetime import datetime

from perfin.util import make_key

TEST_FILE_DIR = "{}/files".format(os.path.dirname(os.path.abspath(__name__)))

"""
    how to run

    make test TEST_FILE=test_parsing
"""


def test_parsing_key():
    """
        how to run

        make test TEST_FILE=test_parsing TEST_FN=test_parsing_key
    """

    assert make_key("45540 VERTICAL K DIR DEP 66 011521") == "VERTICALKD"
    assert make_key("HEROKU JUL-39703527") == "HEROKUJUL"
    assert make_key("Prime Video*3H5G70UV3") == "PRIMEVIDEO"
    assert make_key("TST* ON THE RISE ARTISAN") == "TSTONTHER"
    assert make_key("APPLE.COM/BILL",) == "APPLECOM"
    assert make_key("PHO &amp; RICE") == "PHOAMPRI"


def test_basic_schema_capone(csv_docs):
    """
        how to run

        make test TEST_FILE=test_parsing TEST_FN=test_basic_schema_capone
    """

    for row in csv_docs("capone_test_basic"):
        doc = row["doc"]
        assert doc
        assert row["doc_key"] == "capital_one"
        assert isinstance(doc["transaction_posted_date"], datetime)
        assert doc["amount"] < 0


def test_basic_schema_53(csv_docs):
    """
        how to run

        make test TEST_FILE=test_parsing TEST_FN=test_basic_schema_53
    """

    for row in csv_docs("fifththird_test_basic"):
        doc = row["doc"]
        assert doc
        assert row["doc_key"] == "fifth_third"
        assert isinstance(doc["transaction_posted_date"], datetime)
        assert doc["amount"] < 0


def test_basic_chase(csv_docs):
    """
        how to run

        make test TEST_FILE=test_parsing TEST_FN=test_basic_chase
    """

    for row in csv_docs("chase_test_basic"):
        doc = row["doc"]
        assert doc
        assert row["doc_key"] == "chase"
        assert isinstance(doc["transaction_posted_date"], datetime)
        assert doc["amount"] < 0


def test_get_transactions(csv_docs):
    """
        how to run

        make test TEST_FILE=test_parsing TEST_FN=test_get_transactions
    """

    for row in csv_docs("chase____2020.01.01"):
        doc = row["doc"]
        doc_key = row["doc_key"]
        try:
            assert isinstance(doc["amount"], float)
            assert isinstance(doc["description"], str)
            assert isinstance(doc["transaction_posted_date"], datetime)
            assert isinstance(doc["category"], str) or doc["category"] is None
        except (AssertionError, KeyError) as e:
            raise Exception(f"{doc_key}, {doc}") from e
