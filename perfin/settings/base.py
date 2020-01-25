import json
import logging
import logging.config
import os
from urllib.parse import urlparse

from cmreslogging.handlers import CMRESHandler

import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

logger = logging.getLogger(__name__)

ENV = os.environ.get('PERFIN_ENV', 'base').lower()
PERFIN_CLI = os.environ.get('PERFIN_CLI')
SETTINGS_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
PERFIN_CONFIG = '{}/config/{}.json'.format(SETTINGS_DIR, ENV.lower())


def configure_logging():
    es_node = os.environ.get('ES_NODE')
    es_user = os.environ.get('ES_USER')
    es_pass = os.environ.get('ES_PASS')
    es_node = os.environ.get('ES_NODE')
    parsed = urlparse(es_node)
    es_url = parsed.hostname
    es_port = parsed.port
    if parsed.scheme == 'https':
        use_ssl = True
    else:
        use_ssl = False

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
            },
            'elasticsearch' : {
                'class': 'cmreslogging.handlers.CMRESHandler',
                'hosts': [
                    {
                        'host': es_url,
                        'port' : es_port,
                    }
                ],
                'auth_details' : (es_user, es_pass),
                'es_index_name': 'perfin_app_logs',
                'es_additional_fields': {'enviornment': ENV},
                'auth_type': CMRESHandler.AuthType.BASIC_AUTH,
                'use_ssl': use_ssl,
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
            'perfin.lib' : {
                'level': 'INFO'
            },
            'perfin.settings.base' : {
                'handlers' : ['elasticsearch'],
                'level' : 'INFO'
            }
        }
    }

    logging.config.dictConfig(config)


def configure_app():
    configure_env()
    configure_logging()
    if not PERFIN_CLI:
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


def load_settings():
    return {
        'CLIENT_ID' : os.environ.get('CLIENT_ID'),
        'SECRET' : os.environ.get('SECRET'),
        'PUBLIC_KEY' : os.environ.get('PUBLIC_KEY'),
        'PLAID_ENV' : os.environ.get('PLAID_ENV'),
        'INDEX' : os.environ.get('INDEX'),
        'ES_NODE' : os.environ.get("ES_NODE"),
        'ES_USER' : os.environ.get("ES_USER"),
        'ES_PASS' : os.environ.get("ES_PASS")
    }
