import hashlib
import json
import logging
import logging.config
import os
import threading
import uuid

import coloredlogs
from perfin.exceptions import MalformedParams

local = threading.local()

logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        env = os.environ.get("STAGE", "dev")
        full_path = self.find_config_file(env)

        self.configure_logging()
        self.ENV = env
        self.ES_NODE = os.environ.get("ES_NODE", "http://localhost:9200")
        self.ES_USER = os.environ.get("ES_USER")
        self.ES_PASS = os.environ.get("ES_PASS")
        self.ES_NODE = os.environ.get("ES_NODE")

        self.body = {}

        if os.path.exists(full_path):
            self._full_path = full_path
        else:
            raise Exception("config file not found!!!")

        self.init_file(full_path)

    def generate_better_key(self):
        hash_object = hashlib.sha256(str(uuid.uuid4()).encode("utf8"))
        hex_dig = hash_object.hexdigest()
        return hex_dig

    def generate_specific_key(self, *args):
        key_string = "".join([*args]).encode("utf-8")
        hash_object = hashlib.sha256(key_string)
        hex_dig = hash_object.hexdigest()
        return hex_dig

    def create_file_name(self, account, from_date, to_date):
        key = self.generate_better_key()[0:10]
        return "{}____{}-{}____{}".format(account, from_date, to_date, key)

        def validate(self, keys):
            kwargs = self.init_kwargs
            if isinstance(kwargs, dict):
                kwarg_keys = list(kwargs.keys())
                listed = [
                    key for key in keys if kwargs.get(key) or kwargs.get(key) == 0
                ]
                if len(kwarg_keys) != len(listed):
                    raise MalformedParams(
                        "{} {} {}".format(self.__class__.__name__, kwarg_keys, listed)
                    )

    def init_file(self, full_path):
        with open(full_path, "r+") as file:
            logger.info("found {}".format(self._full_path))
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
