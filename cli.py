import sys
from pathlib import Path

from perfin import PathFinder, Transaction, get_transactions, move_files
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
    if Transaction._index.exists():
        Transaction._index.delete()


def reboot_index():
    """
        How to run

        make cli CMD=reboot_index
    """
    destroy_index()
    create_index()


def sync_s3_data_locally():
    """
        How to run

        make cli CMD=sync_s3_data_locally
    """
    finder = PathFinder(s3_bucket_path="mzakany-perfin")
    for t in get_transactions(finder):
        trans = Transaction(**t.doc)
        trans.save()


def insert_transactions():
    """
        How to run

        make cli CMD=insert_transactions
    """
    path = config.root_path.joinpath("files")
    finder = PathFinder(csv_path=path)
    for t in get_transactions(finder):
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


def reindex_index():
    """
        How to run

        make cli CMD=reindex_index
    """
    reboot_index()
    move_files_to_root()
    insert_transactions()


def run():
    """
        How to run

        make cli CMD=run
    """
    print("do something here")


if __name__ == "__main__":
    args = sys.argv
    try:
        getattr(__import__("__main__"), args[1])()
    except IndexError:
        run()
