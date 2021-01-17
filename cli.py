import sys
from pathlib import Path

from perfin import Transaction, get_transactions, move_files
from perfin.settings import config


def schema_fields():
    """
        How to run

        make cli CMD=schema_fields

        Description

        Show me what the schema should look like
    """
    lookup = set()
    for k, v in config.ACCOUNT_LOOKUP.items():
        for item in v["file_columns"]:
            k = item["key"]
            t = item["schema_type"]
            lookup.add(f"{k}:{t}")
    print("----------------")
    print("fields")
    print("----------------")
    print()
    for item in lookup:
        print(item)


def create_index():
    """
        How to run

        make cli CMD=create_index
    """
    Transaction.init()


def destroy_index():
    """
        How to run

        make cli CMD=destroy_index
    """
    Transaction._index.delete()


def reboot_index():
    """
        How to run

        make cli CMD=reboot_index
    """
    destroy_index()
    create_index()


def reindex_index():
    """
        How to run

        make cli CMD=reindex_index
    """
    reboot_index()
    move_files_to_root()
    insert_transactions()


def insert_transactions():
    """
        How to run

        make cli CMD=insert_transactions
    """
    path = config.root_path.joinpath("files")

    for t in get_transactions(path):
        trans = Transaction(**t.doc)
        trans.save()


def move_files_to_root():
    """
        How to run

        make cli CMD=move_files_to_root

        Description

        Move all files from directory that match accounts.json
        into files folder
    """
    path = Path("~/Desktop").expanduser()
    move_files(path)


def run():
    """
        How to run

        make cli CMD=run
    """
    print("do something")


if __name__ == "__main__":
    args = sys.argv
    try:
        getattr(__import__("__main__"), args[1])()
    except IndexError:
        run()
