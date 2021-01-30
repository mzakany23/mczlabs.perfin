import datetime

import pytest
from perfin.csv import Row

DEFAULT_FIELD_PARAMS = [
    {
        "column_name": "Date",
        "sort_key": True,
        "date_format": "%m/%d/%Y",
        "key": "transaction_posted_date",
        "schema_type": "date",
        "original_value": "01/04/2019",
        "processed_value": datetime.datetime(2019, 1, 4, 0, 0),
    },
    {
        "column_name": "Description",
        "key": "description",
        "schema_type": "string",
        "original_value": "EAST OHIO GAS PAYMENT XXXXXXXXXXX0161 010419",
        "processed_value": "EAST OHIO GAS PAYMENT XXXXXXXXXXX0161 010419",
    },
    {
        "column_name": "Check Number",
        "key": "check_num",
        "schema_type": "int",
        "original_value": "",
        "processed_value": 0,
    },
    {
        "column_name": "Amount",
        "key": "amount",
        "schema_type": "float",
        "original_value": -87.0,
        "processed_value": -87.0,
    },
]


@pytest.fixture
def row_factory():
    def inner(
        account_name="someaccountname",
        account_type="someaccounttype",
        row=DEFAULT_FIELD_PARAMS,
    ):
        return Row(account_name, account_type, row)

    return inner
