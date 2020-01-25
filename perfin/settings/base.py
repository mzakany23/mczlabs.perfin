import json
import logging
import logging.config
import os


logger = logging.getLogger(__name__)


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
            'perfin.settings.base' : {
                'level': 'INFO'
            },
            'perfin.lib' : {
                'level': 'INFO'
            }
        }
    }

    logging.config.dictConfig(config)

CLIENT_ID = os.environ.get('CLIENT_ID')
SECRET = os.environ.get('SECRET')
PUBLIC_KEY = os.environ.get('PUBLIC_KEY')
PLAID_ENV = os.environ.get('PLAID_ENV')
ENV = os.environ.get('PERFIN_ENV', 'BASE')

try:
    ACCOUNT_LOOKUP = json.loads(os.environ.get('ACCOUNT_LOOKUP'))
except:
    ACCOUNT_LOOKUP = None


def configure_app():
    configure_logging()
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    filename = '{}/config/{}.json'.format(root_dir, ENV.lower())
    logger.debug("gathering {}'s environment variables...".format(ENV))
    with open(filename, 'r') as f:
        file = json.load(f)
        logger.debug(file)
        logger.debug('environment:\n'.format(file))
