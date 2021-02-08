import datetime
import hashlib
import json
import threading
import uuid
from pathlib import Path

local = threading.local()

DATE_FMT = "%Y-%m-%d"
ES_DATE_FMT = "yyyy-MM-dd"
ES_CONFIG = {"hosts": ["localhost"], "timeout": 20}


class Config:
    def __init__(self):
        self.init_config()

    @property
    def date_fmt(self):
        return DATE_FMT

    @property
    def es_date_fmt(self):
        return ES_DATE_FMT

    @property
    def es_config(self):
        return ES_CONFIG

    @property
    def root_path(self):
        path = Path(".").parent.resolve()
        return path.joinpath("perfin") if path.stem.lower() != "perfin" else path

    def generate_better_key(self):
        hash_object = hashlib.sha256(str(uuid.uuid4()).encode("utf8"))
        hex_dig = hash_object.hexdigest()
        return hex_dig

    def generate_specific_key(self, *args):
        key_string = "".join([*args]).encode("utf-8")
        hash_object = hashlib.sha256(key_string)
        hex_dig = hash_object.hexdigest()
        return hex_dig

    def create_file_name(self, name, from_date, to_date):
        if "/" in from_date:
            from_date = from_date.replace("/", ".")
        if "/" in to_date:
            to_date = to_date.replace("/", ".")
        key = self.generate_better_key()[0:10]
        return f"{name}____{from_date}--{to_date}____{key}"

    def init_config(self):
        root = self.root_path.joinpath("config")
        paths = root.glob("*.json")
        if not paths:
            raise Exception(f"There are no configs set at {root}")
        for path in paths:
            with path.open("r+") as file:
                inner = json.load(file)
                for k, v in inner.items():
                    setattr(self, k, v)
        return self

    def dfmt(self, d):
        return None if d is None else datetime.datetime.strftime(d, self.date_fmt)


try:
    config = local.config
except AttributeError:
    config = Config()
    local.config = config
