import datetime
import logging
import re
from dataclasses import dataclass
from typing import Any

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
    account_type: str
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

    def _make_key(self, description):
        desc = re.sub(r"\d+", "", description)
        desc = re.sub(r"\s+", "", desc)[0:10].upper()
        for key in ["*", "-", "&", "/", ".", ";"]:
            desc = desc.replace(key, "")
        return desc

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
