import logging

from .settings import config

logger = logging.getLogger(__name__)


def get_sort_key(account):
    fc = account if isinstance(account, list) else account["file_columns"]
    for col in fc:
        if isinstance(col, list):
            return get_sort_key(col)
        if col.get("sort_key"):
            return col
    raise Exception(f"could not find a sort_key attr in {fc}")


def find_account(search_name):
    for account_name, account_config in config.ACCOUNT_LOOKUP.items():
        for account_alias in account_config["file_name_search"]:
            alias_match = account_alias.lower() in search_name
            if alias_match:
                account_config["account_name"] = account_name
                return account_config
