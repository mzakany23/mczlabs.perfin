import datetime
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas

from .exceptions import PerfinColumnParseError
from .settings import config

logger = logging.getLogger(__name__)


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

    def _get_field(self, field: Any, coerce_type: Any = None):
        item = None
        if hasattr(self, field):
            item = getattr(self, field).processed_value
        if item and coerce_type:
            return coerce_type(item)
        return item

    @property
    def pamount(self):
        if hasattr(self, "amount"):
            val = self.amount.processed_value
        elif hasattr(self, "debit"):
            val = self.debit.processed_value * -1
        elif hasattr(self, "credit"):
            val = self.credit.processed_value * -1
        return float(val)

    @property
    def doc(self):
        description = self._get_field("description")
        return {
            "category": self._get_field("category"),
            "key": re.sub(r"\s+", "", description)[0:12],
            "account": self.account_name,
            "amount": self.pamount,
            "description": description,
            "check_num": self._get_field("check_num", int),
            "date": self._get_field("transaction_posted_date"),
            "posted_date": self._get_field("transaction_posted_date"),
            "trans_date": self._get_field("transaction_date"),
            "trans_type": self._get_field("transaction_type"),
            "credit": self._get_field("credit"),
            "memo": self._get_field("memo"),
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
            try:
                assert len(df.columns) == len(file_columns)
            except AssertionError:
                cols = [col for col in df.columns]
                spec = [f["key"] for f in file_columns]
                raise PerfinColumnParseError(
                    f"column error! Data frame shows {len(cols)} columns\ndf columns: {cols} \nspec columns: {spec}"
                )

            for i, stype in enumerate(file_columns):
                stype["original_value"] = row[i]
                stype["processed_value"] = convert_field(row[i], stype)
                row[i] = stype

            yield Row(account["account_name"], row)


def load_files(base_path: Path = None, patterns=["*.csv"]):
    for pattern in patterns:

        for path in base_path.glob(pattern):
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
                logger.warning(f"could not match file alias {path.name.lower()}")
                continue

            yield account, path, df


def get_file_names(path: Path, ext_globs=["*.csv"], new_file_ext="csv"):
    for account, path, df in load_files(path, ext_globs):
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
        new_file_name = f"{config.create_file_name(account_name, start_date, end_date)}.{new_file_ext}"
        yield path, new_file_name


def move_files(path: Path):
    for file, new_file_name in get_file_names(path, ["*.csv", "*.CSV"]):
        nfp = config.root_path.joinpath(f"files/{new_file_name}")
        file.rename(nfp)
        logger.info(f"successfully moved {nfp}")
