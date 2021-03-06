import json
import os
import sys
from pathlib import Path

from loguru import logger
from perfin import (
    LocalCSVFileFinder,
    PerFinTransaction,
    S3CSVFileFinder,
    csv_docs,
    get_csv_file_names,
)

FILE_DIR = os.environ.get("FILE_DIR", Path("./files").resolve())
BUCKET_PATH = os.environ.get("BUCKET_PATH", "mzakany-perfin")
BASE_PATH = "~/Desktop"

path = Path("./.config/accounts.json").resolve()

with path.open("r") as file:
    SCHEMA = json.load(file)


def stop():
    """
        How to run

        make cli CMD=start
    """
    os.system(f"cd {BASE_PATH}/perfin;TAG=7.10.2 docker-compose down --remove-orphans")


def start():
    """
        How to run

        make cli CMD=start
    """
    os.system(f"cd {BASE_PATH}/perfin;TAG=7.10.2 docker-compose up --remove-orphans")


def create_index():
    """
        How to run

        make cli CMD=create_index
    """
    PerFinTransaction.init()


def destroy_index():
    """
        How to run

        make cli CMD=destroy_index
    """
    if PerFinTransaction._index.exists():
        PerFinTransaction._index.delete()


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
    for row in csv_docs(
        base_path=BUCKET_PATH, schema=SCHEMA, finder_cls=S3CSVFileFinder
    ):
        PerFinTransaction.create(**row)


def insert_transactions():
    """
        How to run

        make cli CMD=insert_transactions
    """
    for row in csv_docs(
        base_path=FILE_DIR, schema=SCHEMA, finder_cls=LocalCSVFileFinder
    ):
        PerFinTransaction.create(**row)


def move_files_to_root():
    """
        How to run

        make cli CMD=move_files_to_root

        Description

        Move all files from directory that match accounts.json
        into files folder
    """
    finder = LocalCSVFileFinder(base_path=BASE_PATH)

    for old_file, new_file_name in get_csv_file_names(finder, FILE_DIR, SCHEMA):
        old_file.rename(new_file_name)


def move_files_to_s3():
    """
        How to run

        make cli CMD=move_files_to_s3
    """

    s3_finder = S3CSVFileFinder(base_path=BUCKET_PATH)

    local_finder = LocalCSVFileFinder(base_path=FILE_DIR)

    for local_file in local_finder.load_files():
        logger.info(f"moving {local_file} to s3")
        s3_finder.move(local_file)
        logger.info("done.")


def delete_local_files():
    """
        How to run

        make cli CMD=delete_local_files
    """
    finder = LocalCSVFileFinder(base_path=FILE_DIR)

    for path in finder.load_files():
        logger.info(f"deleting {path}")
        path.unlink()
        logger.info("done")


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
