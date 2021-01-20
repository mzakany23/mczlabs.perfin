import logging

from .settings import config

logger = logging.getLogger(__name__)


def find_account(search_name):
    for account_name, account_config in config.ACCOUNT_LOOKUP.items():
        for account_alias in account_config["file_name_search"]:
            alias_match = account_alias.lower() in search_name

            if alias_match:
                account_config["account_name"] = account_name
                return account_config
