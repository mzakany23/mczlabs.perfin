import json
import logging
import logging.config
import os

import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

from perfin.lib.models import PerfinAccount

logger = logging.getLogger(__name__)

ENV = os.environ.get('PERFIN_ENV', 'base').lower()
SETTINGS_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
PERFIN_CONFIG = '{}/config/{}.json'.format(SETTINGS_DIR, ENV.lower())


def configure_logging():
    config = {
        'version': 1,
        'formatters': {
            'simple': {
                'format': '[%(asctime)s] [%(name)s|%(levelname)s@%(filename)s:%(lineno)d] %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            }
        },
        'root': {
            'level': 'ERROR',
            'handlers': ['console']
        },
        'loggers': {
            'perfin.util.es.es_conn': {
                'level': 'INFO'
            },
            'perfin.lib.models.base' : {
                'level': 'INFO'
            },
            'perfin.settings.base' : {
                'level': 'INFO'
            },
            'perfin.lib' : {
                'level': 'INFO'
            }
        }
    }

    logging.config.dictConfig(config)


def configure_app():
    configure_logging()
    configure_env()
    configure_sentry()
    log_env()


def configure_sentry():
    sentry_key = os.environ.get('SENTRY_KEY')

    if sentry_key:
        sentry_sdk.init(dsn=sentry_key, debug=True, integrations=[AwsLambdaIntegration()])


def configure_env():
    with open(PERFIN_CONFIG, 'r') as f:
        file = json.load(f)
        for k, v in file.items():
            os.environ.setdefault(k, str(v))


def log_env():
    logger.debug("enviornment:PERFIN_ENV={}".format(ENV))
    logger.debug(PERFIN_CONFIG)


configure_app()


CLIENT_ID = os.environ.get('CLIENT_ID')
SECRET = os.environ.get('SECRET')
PUBLIC_KEY = os.environ.get('PUBLIC_KEY')
PLAID_ENV = os.environ.get('PLAID_ENV')

INDEX = os.environ.get('INDEX')
ES_NODE = os.environ.get("ES_NODE")
ES_USER = os.environ.get("ES_USER")
ES_PASS = os.environ.get("ES_PASS")
