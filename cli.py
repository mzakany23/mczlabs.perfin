import os
import sys
from pathlib import Path

from perfin import PathFinder, Transaction, get_transactions, move_files
from perfin.s3 import get_s3_conn
from perfin.settings import config


def start():
    """
        How to run

        make cli CMD=start
    """
    os.system("TAG=7.10.2 docker-compose up --remove-orphans")


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
    finder = PathFinder(s3_bucket_path=config.AWS["bucket_path"])
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
    finder = PathFinder(csv_path=path)
    move_files(finder)


def move_files_to_s3():
    """
        How to run

        make cli CMD=move_files_to_s3
    """
    path = config.root_path.joinpath("files")
    finder = PathFinder(csv_path=path)
    bucket = config.AWS["bucket_path"]
    for path in finder.paths:
        filename = f"{bucket}/{path.name}"
        get_s3_conn().put(str(path), filename)


def delete_local_files():
    """
        How to run

        make cli CMD=delete_local_files
    """
    path = config.root_path.joinpath("files")
    finder = PathFinder(csv_path=path)
    for path in finder.paths:
        path.unlink()


def reindex_index():
    """
        How to run

        make cli CMD=reindex_index
    """
    reboot_index()
    move_files_to_root()
    insert_transactions()


def move_ingest_and_delete():
    """
        How to run

        make cli CMD=move_ingest_and_delete
    """
    move_files_to_root()
    insert_transactions()
    move_files_to_s3()
    delete_local_files()


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
