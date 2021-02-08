import datetime
import re
from dataclasses import dataclass
from typing import Dict, List, Union


def _key(description):
    desc = re.sub(r"\d+", "", description)
    desc = re.sub(r"\s+", "", desc)[0:10].upper()
    for key in ["*", "-", "&", "/", ".", ";"]:
        desc = desc.replace(key, "")
    return desc


@dataclass
class RowField:
    column_index: int = None
    column_name: str = None
    key: str = None
    original_value: Union[float, str, int, datetime.datetime] = None
    processed_value: Union[float, str, int, datetime.datetime] = None
    date_format: str = None
    schema_type: str = None
    invert_value: bool = False
    sort_key: str = None


@dataclass
class Row:
    account_name: str
    account_type: str
    row: List[Dict]

    def __post_init__(self):
        if not isinstance(self.row, list):
            raise Exception(
                f"error with {self.account_name}, row {self.row} is not a list!"
            )

        if not self.account_name:
            raise Exception(f"account name '{self.account_name}' can't be None")

        if not self.account_type:
            raise Exception(f"account type '{self.account_name}' can't be None")

        for i, field in enumerate(self.row):
            field = RowField(**field)
            setattr(self, field.key, field)

    def _get_field(self, field: RowField, coerce_type: Union[int, float, str] = None):
        item = getattr(self, field, None)
        if item:
            item = item.processed_value

        if item and coerce_type:
            return coerce_type(item)
        return item

    def _make_key(self, description):
        return _key(description)

    @property
    def pamount(self):
        val = 0
        if hasattr(self, "amount"):
            val = self.amount.processed_value
        elif hasattr(self, "debit"):
            val = self.debit.processed_value * -1
        elif hasattr(self, "credit"):
            val = self.credit.processed_value * -1
        return float(val)

    @property
    def doc(self):
        description = self._get_field("description") or ""

        return {
            "category": self._get_field("category"),
            "key": self._make_key(description),
            "account_name": self.account_name,
            "account_type": self.account_type,
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


def convert_date(value, stype):
    if isinstance(stype, list):
        for fmt in stype:
            try:
                return datetime.datetime.strptime(value, fmt)
            except ValueError:
                continue
            else:
                raise
    elif isinstance(stype, str):
        return datetime.datetime.strptime(value, stype)
    else:
        return datetime.datetime.strptime(value, stype["original_value"])


def convert_int(value, stype):
    value = value or 0
    return int(value)


def convert_float(value, stype):
    value = value or 0.0
    calc = float(value)
    if stype.get("invert_value"):
        calc *= -1.0
    return calc


def convert_field(value: str, stype: dict):
    field_lookup = {"date": convert_date, "float": convert_float, "int": convert_int}

    fn = field_lookup.get(stype["schema_type"])

    return value if not fn else fn(value, stype)
