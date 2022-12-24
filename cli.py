import json
import os
import sys

from loguru import logger
from perfin import (LocalCSVFileFinder, S3CSVFileFinder, config,
                    csv_doc_batches, csv_docs, get_csv_file_names, get_es)
from perfin.models import create_pg_docs, create_pg_tables

BASE_PATH = config.base_path
BUCKET_PATH = config.bucket_path
FILE_DIR = config.file_dir
SCHEMA = config.schema()

ES = get_es()


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
    ES.init()


def destroy_index():
    """
        How to run

        make cli CMD=destroy_index
    """
    if ES._index.exists():
        ES._index.delete()


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
        ES.create(**row)


def insert_transactions():
    """
        How to run

        make cli CMD=insert_transactions
    """
    for row in csv_docs(
        base_path=FILE_DIR, schema=SCHEMA, finder_cls=LocalCSVFileFinder
    ):
        ES.create(**row)


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


def show_flat_batches():
    """
        How to run

        make cli CMD=show_flat_batches
    """
    for partition, batch in enumerate(csv_doc_batches(1)):
        for flat_row in batch:
            print(flat_row)


def show_merged_headers():
    """
        How to run

        make cli CMD=show_merged_headers
    """
    unique = set()
    for partition, batch in enumerate(csv_doc_batches(1)):
        for flat_row in batch:
            # print(flat_row)
            cols = set([
                column['column_name']for column
                in json.loads(flat_row.original)["file_column"]
            ])
            unique = unique.union(cols)
    print(f"total headers: {unique}")


def setup_pg():
    """
        How to run

        make cli CMD=setup_pg
    """
    create_pg_tables()


def ingest_pg():
    """
        How to run

        make cli CMD=ingest_pg

        Description

        Ensure `setup_pg` ran first
    """
    ingested = 0
    for batch in csv_doc_batches(200):
        create_pg_docs(batch)
        ingested += len(batch)
        logger.info(f"batch: {ingested}")


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
