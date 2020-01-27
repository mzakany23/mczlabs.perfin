import logging

logger = logging.getLogger(__file__)

from perfin.settings.base import configure_app

configure_app()

'''
    DESCRIPTION
        AWS_PROFILE=mzakany DEACTIVATE_SENTRY=1 PERFIN_ENV=local python query.py
        AWS_PROFILE=mzakany DEACTIVATE_SENTRY=1 PERFIN_ENV=dev python query.py
        AWS_PROFILE=mzakany DEACTIVATE_SENTRY=1 PERFIN_ENV=prod python query.py

        # defaults to base
        python query.py
'''


if __name__ == '__main__':
    pass
