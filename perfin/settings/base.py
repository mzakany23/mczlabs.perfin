import os
import logging
import logging.config

import json

logger = logging.getLogger('handler')
logger.setLevel(logging.INFO)

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
            'level': 'DEBUG',
            'handlers': ['console']
        },
        'loggers': {
            'es': {
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

try:
    ACCOUNT_LOOKUP = json.loads(os.environ.get('ACCOUNT_LOOKUP'))
except:
    ACCOUNT_LOOKUP = None

from .dev import *
