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


@dataclass
class Config:
    ES_NODE: str
    ES_USER: str
    ES_PASS: str
    ES_NODE: str
    LOCAL_FILE_DIR: str = ""

    def __init__(self):
        env = os.environ.get("STAGE", "dev")

        self.configure_logging()
        self.ENV = env
        self.body = {}
        full_path = os.path.dirname(os.path.abspath(__name__))
        self.init_file("{}/config/{}.json".format(full_path, env))
        if self.LOCAL_FILE_DIR:
            if "~" in self.LOCAL_FILE_DIR:
                self.LOCAL_FILE_DIR = Path(self.LOCAL_FILE_DIR).expanduser()
            else:
                self.LOCAL_FILE_DIR = Path(self.LOCAL_FILE_DIR)

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
        return "{}____{}-{}____{}".format(name, from_date, to_date, key)

    def init_file(self, full_path):
        with open(full_path, "r+") as file:
            logger.info("found {}".format(full_path))
            self.body = json.load(file)
            for k, v in self.body.items():
                setattr(self, k, v)
            logger.info("file contents {}".format(self.body))
            return self

    def find_config_file(self, env):
        logger.info("Looking for: %s" % env)
        directory = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        file_path = "{}/configs/{}.json".format(directory, env)
        return file_path

    def configure_logging(self):
        config = {
            "version": 1,
            "formatters": {
                "simple": {
                    "format": "[%(asctime)s] [%(name)s|%(levelname)s@%(filename)s:%(lineno)d] %(message)s"
                }
            },
            "handlers": {
                "console": {"class": "logging.StreamHandler", "formatter": "simple"}
            },
            "root": {"level": "DEBUG", "handlers": ["console"]},
            "loggers": {
                "selenium": {"level": "INFO"},
                "pynamodb": {"level": "INFO"},
                "s3transfer": {"level": "INFO"},
                "botocore": {"level": "INFO"},
                "boto3": {"level": "INFO"},
            },
        }
        logging.config.dictConfig(config)
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
