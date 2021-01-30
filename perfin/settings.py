import datetime
import hashlib
import json
import logging
import logging.config
import threading
import uuid
from pathlib import Path

import coloredlogs

local = threading.local()

logger = logging.getLogger(__name__)

DATE_FMT = "%Y-%m-%d"
ES_DATE_FMT = "yyyy-MM-dd"
ES_CONFIG = {"hosts": ["localhost"], "timeout": 20}
COLOR_LOGS = {
    "level": "DEBUG",
    "fmt": "[%(asctime)s] [%(name)s|%(levelname)s@%(filename)s:%(lineno)d] %(message)s",
    "level_styles": {
        "critical": {"bold": True, "color": "red"},
        "debug": {"color": "blue"},
        "error": {"color": "red"},
        "info": {"color": "green"},
        "notice": {"color": "magenta"},
        "spam": {"color": "green", "faint": True},
        "success": {"bold": True, "color": "green"},
        "verbose": {"color": "blue"},
        "warning": {"color": "yellow"},
    },
    "field_styles": {
        "asctime": {"color": "magenta"},
        "hostname": {"color": "magenta"},
        "message": {"color": "green", "bold": True},
        "levelname": {"bold": True, "color": "green"},
        "name": {"color": "blue"},
        "programname": {"color": "cyan"},
        "username": {"color": "yellow"},
    },
}

LOGGING_CONFIG = config = {
    "version": 1,
    "formatters": {
        "simple": {
            "format": "[%(asctime)s] [%(name)s|%(levelname)s@%(filename)s:%(lineno)d] %(message)s"
        }
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "simple"}},
    "root": {"level": "DEBUG", "handlers": ["console"]},
    "loggers": {
        "selenium": {"level": "INFO"},
        "pynamodb": {"level": "INFO"},
        "s3transfer": {"level": "INFO"},
        "botocore": {"level": "INFO"},
        "boto3": {"level": "INFO"},
    },
}


class Config:
    def __init__(self):
        self.configure_logging()
        self.init_file()

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

    def init_file(self):
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

    def configure_logging(self):
        logging.config.dictConfig(LOGGING_CONFIG)
        coloredlogs.install(**COLOR_LOGS)


try:
    config = local.config
except AttributeError:
    config = Config()
    local.config = config
