import hashlib
import json
import logging
import logging.config
import os
import threading
import uuid
from dataclasses import dataclass
from pathlib import Path

import coloredlogs

local = threading.local()

logger = logging.getLogger(__name__)

DATE_FMT = "%Y-%m-%d"
ACCOUNTS_CONFIG_FILE = "config/accounts.json"
FILES_PATH = "files"
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


@dataclass
class Config:
    ES_NODE: str
    ES_USER: str
    ES_PASS: str
    body: dict

    def __init__(self):
        self.configure_logging()
        self.init_file()

    def __post_init__(self):
        for attr in ["ES_NODE", "ES_USER", "ES_PASS"]:
            config = getattr(self, attr)
            if not config:
                setattr(self, attr, os.environ.get(attr))

    @property
    def date_fmt(self):
        return DATE_FMT

    @property
    def csv_files(self):
        return self.root.joinpath("files").glob("*.csv")

    @property
    def root(self):
        return Path(".").parent.resolve()

    @property
    def files_path(self):
        return self.root.joinpath(FILES_PATH)

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
        return f"{name}____{from_date}-{to_date}____{key}"

    def init_file(self):
        full_path = self.root.joinpath(ACCOUNTS_CONFIG_FILE)
        with full_path.open("r+") as file:
            self.body = json.load(file)
            for k, v in self.body.items():
                setattr(self, k, v)
            return self

    def configure_logging(self):
        logging.config.dictConfig(LOGGING_CONFIG)
        coloredlogs.install(
            level="DEBUG",
            fmt="[%(asctime)s] [%(name)s|%(levelname)s@%(filename)s:%(lineno)d] %(message)s",
            level_styles={
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
            field_styles={
                "asctime": {"color": "magenta"},
                "hostname": {"color": "magenta"},
                "message": {"color": "green", "bold": True},
                "levelname": {"bold": True, "color": "green"},
                "name": {"color": "blue"},
                "programname": {"color": "cyan"},
                "username": {"color": "yellow"},
            },
        )


try:
    config = local.config
except AttributeError:
    config = Config()
    local.config = config
