import logging

logger = logging.getLogger(__file__)

from perfin.settings.base import configure_app

configure_app()

'''
    DESCRIPTION
        PERFIN_ENV=local python query.py
        PERFIN_ENV=dev python query.py

        # defaults to base
        python query.py
'''

if __name__ == '__main__':
    pass