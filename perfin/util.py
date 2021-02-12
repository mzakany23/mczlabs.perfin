import hashlib
import re
import uuid
from datetime import datetime


def generate_better_key(self):
    hash_object = hashlib.sha256(str(uuid.uuid4()).encode("utf8"))
    hex_dig = hash_object.hexdigest()
    return hex_dig


def generate_specific_key(self, *args):
    key_string = "".join([*args]).encode("utf-8")
    hash_object = hashlib.sha256(key_string)
    hex_dig = hash_object.hexdigest()
    return hex_dig


def convert_date(value, stype):
    if isinstance(stype, list):
        for fmt in stype:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
            raise Exception(f"could not convert date {stype}")
    elif isinstance(stype, str):
        return datetime.strptime(value, stype)

    return datetime.strptime(value, stype["original_value"])


def create_file_name(name, from_date, to_date):
    if "/" in from_date:
        from_date = from_date.replace("/", ".")
    if "/" in to_date:
        to_date = to_date.replace("/", ".")
    key = generate_better_key()[0:10]
    return f"{name}____{from_date}--{to_date}____{key}"


def convert_int(value, stype):
    value = value or 0
    return int(value)


def convert_float(value, stype):
    value = value or 0.0
    calc = float(value)
    if stype.get("invert_value"):
        calc *= -1.0
    return calc


def make_key(description):
    desc = re.sub(r"\d+", "", description)
    desc = re.sub(r"\s+", "", desc)[0:10].upper()
    for key in ["*", "-", "&", "/", ".", ";"]:
        desc = desc.replace(key, "")
    return desc
