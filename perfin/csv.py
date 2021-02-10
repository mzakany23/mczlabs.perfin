import datetime
import re
from typing import Callable, List, Set

from pydantic.dataclasses import dataclass

from .types import ALIAS_FIELD_NAME, DateFormat, RowFieldValue, SchemaType


def convert_date(value, stype):
    if isinstance(stype, list):
        for fmt in stype:
            try:
                return datetime.datetime.strptime(value, fmt)
            except ValueError:
                continue
            raise Exception(f"could not convert date {stype}")
    elif isinstance(stype, str):
        return datetime.datetime.strptime(value, stype)

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


def make_key(description):
    desc = re.sub(r"\d+", "", description)
    desc = re.sub(r"\s+", "", desc)[0:10].upper()
    for key in ["*", "-", "&", "/", ".", ";"]:
        desc = desc.replace(key, "")
    return desc


@dataclass
class RowField:
    column_name: str = None
    key: str = None
    original_value: RowFieldValue = None
    processed_value: RowFieldValue = None
    date_format: DateFormat = None
    schema_type: SchemaType = None
    invert_value: bool = False
    alias: str = None
    sort_key: bool = None


@dataclass
class Row:
    account_name: str
    account_type: str
    field_lookup: dict
    schema_keys: Set[str]
    processed_fields: List[RowField]

    __all__ = {
        "category",
        "transaction_type",
        "memo",
        "check_num",
        "transaction_date",
        "card_num",
        "debit",
        "credit",
        "transaction_posted_date",
        "description",
        "amount",
    }
    __non_dynamic__ = ["account_name", "account_type"]

    @property
    def alias_lookup(self):
        return self.field_lookup.get(ALIAS_FIELD_NAME, {})

    def __getattr__(self, attr):
        return (
            getattr(self, attr)
            if attr in self.__non_dynamic__
            else self.get_field(attr)
        )

    def get_field(
        self,
        field_key: str,
        default: RowFieldValue = None,
        coerce_type: Callable = None,
    ):
        item_key = self.field_lookup.get(field_key, default)
        item = None

        if item_key is None:
            alias_key = self.alias_lookup.get(field_key)
            if alias_key is not None:
                item_key = alias_key

        if item_key is not None:
            item = self.processed_fields[item_key].processed_value
            return coerce_type(item) if coerce_type else item

        return item

    @property
    def doc(self):
        key = self.get_field("description") or ""

        doc = {
            "key": make_key(key),
            "account_name": self.account_name,
            "account_type": self.account_type,
        }
        self.schema_keys |= self.__all__
        fields = {k: self.get_field(k) for k in self.schema_keys}
        fields.update(doc)
        return fields
