import datetime

import pandas
import pytest
from perfin.csv import Row
from perfin.paths import PathFinder

from .util import ROOT_PATH

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
        return Row(account_name, account_type, {}, [], row)

    return inner


@pytest.fixture
def csv_finder():
    def inner(file_name):
        return PathFinder(csv_path=ROOT_PATH.joinpath(f"{file_name}.csv").resolve())

    return inner


@pytest.fixture
def df_finder(csv_finder):
    def inner(file_name="capone_test_basic"):
        finder = csv_finder(file_name)
        path = [path for path in finder.paths][0]
        return pandas.read_csv(f"{path}", keep_default_na=False)

    return inner
