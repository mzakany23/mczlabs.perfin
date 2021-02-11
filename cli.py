import os
import sys
from pathlib import Path

from perfin import PathFinder, Transaction, get_transactions, move_files
from perfin.s3 import get_s3_conn

BUCKET_PATH = os.environ.get("BUCKET_PATH", "mzakany-perfin")
MOVE_FILES_TO_DIR = os.environ.get("MOVE_FILES_TO_DIR", Path("./files").resolve())


def stop():
    """
        How to run

        make cli CMD=start
    """
    os.system("cd ~/Desktop/perfin;TAG=7.10.2 docker-compose down --remove-orphans")


def start():
    """
        How to run

        make cli CMD=start
    """
    os.system("cd ~/Desktop/perfin;TAG=7.10.2 docker-compose up --remove-orphans")


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
    finder = PathFinder(s3_bucket_path=BUCKET_PATH)
    for t in get_transactions(finder):
        trans = Transaction(**t.doc)
        trans.save()


def insert_transactions():
    """
        How to run

        make cli CMD=insert_transactions
    """
    finder = PathFinder(csv_path=MOVE_FILES_TO_DIR)
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
    move_files(finder, MOVE_FILES_TO_DIR)


def move_files_to_s3():
    """
        How to run

        make cli CMD=move_files_to_s3
    """
    finder = PathFinder(csv_path=MOVE_FILES_TO_DIR)

    for path in finder.paths:
        filename = f"{BUCKET_PATH}/{path.name}"
        get_s3_conn().put(str(path), filename)


def delete_local_files():
    """
        How to run

        make cli CMD=delete_local_files
    """

    finder = PathFinder(csv_path=MOVE_FILES_TO_DIR)
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


def upload():
    """
        How to run

        make cli CMD=upload
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
        globals()[args[1]]()
    except IndexError:
        run()
