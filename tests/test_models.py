"""
    how to run

    make test TEST_FILE=test_models
"""
import datetime

from perfin.models import PerFinTransaction, dfmt

now = datetime.datetime.now()


def test_models():
    """
        how to run

        make test TEST_FILE=test_models TEST_FN=test_models
    """

    date = dfmt(now, "%Y-%m-%d")

    assert type(date) == str


def test_create(mocker):
    """
        how to run

        make test TEST_FILE=test_models TEST_FN=test_create
    """
    super_call = mocker.patch("perfin.models.super")
    item = PerFinTransaction()
    item.create(
        doc={
            "description": "foo",
            "transaction_date": now,
            "transaction_posted_date": now,
            "card_num": "foo",
            "category": "foo",
            "original": "foo",
            "debit": "foo",
            "credit": "foo",
            "trans_type": "foo",
            "amount": 0.00,
            "memo": "foo",
            "check_num": "foo",
        },
        doc_key="foo",
        doc_type="foo",
    )
    assert super_call.called
