import datetime
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas

from .settings import config


@dataclass
class RowField:
    column_index: int
    column_name: str
    key: str
    original_value: Any
    processed_value: Any
    date_format: str = None
    schema_type: str = None


@dataclass
class Row:
    account_name: str
    row: dict

    def __post_init__(self):
        for i, field in enumerate(self.row):
            field = RowField(
                column_index=field.get("column_index"),
                column_name=field.get("column_name"),
                key=field.get("key"),
                original_value=field.get("original_value"),
                processed_value=field.get("processed_value"),
                date_format=field.get("date_format"),
                schema_type=field.get("schema_type"),
            )
            setattr(self, field.key, field)

    def _get_field(self, field: str):
        if hasattr(self, field):
            return getattr(self, field).processed_value

    @property
    def ptrans_date(self):
        return self._get_field("transaction_date")

    @property
    def ppost_date(self):
        return self._get_field("transaction_posted_date")

    @property
    def pdate(self):
        return self._get_field("transaction_posted_date")

    @property
    def pdescription(self):
        return self._get_field("description")

    @property
    def pcategory(self):
        return self._get_field("category")

    @property
    def ptransaction_type(self):
        return self._get_field("transaction_type")

    @property
    def pcheck_num(self):
        return self._get_field("check_num")

    @property
    def pamount(self):
        if hasattr(self, "amount"):
            val = self.amount.processed_value
        elif hasattr(self, "debit"):
            val = self.debit.processed_value * -1
        elif hasattr(self, "credit"):
            val = self.credit.processed_value * -1
        return val

    @property
    def doc(self):
        return {
            "category": re.sub(r"\s+", "", self.pdescription)[0:10],
            "account": self.account_name,
            "amount": self.pamount,
            "description": self.pdescription,
            "check_num": self.pcheck_num,
            "date": config.dfmt(self.pdate),
            "posted_date": config.dfmt(self.ppost_date),
            "trans_date": config.dfmt(self.ptrans_date),
            "credit": self._get_field("credit"),
            "debit": self._get_field("debit"),
        }


def convert_field(value: str, stype: dict):
    def _convert_date(value, stype):
        return datetime.datetime.strptime(value, stype["date_format"])

    def _convert_int(value, stype):
        value = value or 0
        return int(value)

    def _convert_float(value, stype):
        value = value or 0.0
        return round(float(value), 2)

    field_lookup = {"date": _convert_date, "float": _convert_float, "int": _convert_int}

    fn = field_lookup.get(stype["schema_type"])

    if not fn:
        return value

    return fn(value, stype)


def get_transactions(path: Path):
    for account, path, df in load_files(path):
        for _, row in df.iterrows():
            file_columns = account["file_columns"]
            assert len(df.columns) == len(file_columns)
            for i, stype in enumerate(file_columns):
                stype["original_value"] = row[i]
                stype["processed_value"] = convert_field(row[i], stype)
                row[i] = stype

            yield Row(account["account_name"], row)


def load_files(path: Path = None):
    paths = config.csv_files if path is None else path.glob("*.csv")

    for path in paths:
        account = None

        df = pandas.read_csv(f"{path}", keep_default_na=False)

        def find_account():
            for account_name, account_config in config.ACCOUNT_LOOKUP.items():
                for account_alias in account_config["search"]:
                    alias_match = account_alias.lower() in path.name.lower()

                    if alias_match:
                        account_config["account_name"] = account_name
                        return account_config

        account = find_account()

        if not account:
            raise Exception(f"could not match file alias {path.name.lower()}")

        yield account, path, df


def get_file_names(path: Path):
    for account, path, df in load_files(path):
        sk = account["sort_key"]
        sort_key = account["file_columns"][sk]
        column_name = sort_key["column_name"]
        dates = df[column_name].to_list()
        date_format = sort_key["date_format"]
        account_name = account["account_name"]
        dates.sort(key=lambda date: datetime.datetime.strptime(date, date_format))
        dates = [datetime.datetime.strptime(date, date_format) for date in dates]
        start_date = datetime.datetime.strftime(dates[0], config.date_fmt)
        end_date = datetime.datetime.strftime(dates[-1], config.date_fmt)
        new_file_path = (
            f"{path}/{config.create_file_name(account_name, start_date, end_date)}.csv"
        )
        new_path = Path(new_file_path)
        yield path, new_path
