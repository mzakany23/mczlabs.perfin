import csv

import pandas
from loguru import logger
from s3fs import S3FileSystem

from .accounts import find_account
from .paths import PathFinder

S3 = None


def get_s3_conn():
    global S3
    return S3 if S3 else S3FileSystem(anon=False)


def get_s3_full_file_paths(directory: str, filter_key: str = None):
    for s3_file_path in get_s3_conn().ls(directory):
        if filter_key:
            if filter_key in s3_file_path:
                yield s3_file_path
        else:
            yield s3_file_path


def get_s3_rows(file_path: str):
    with get_s3_conn().open(file_path, mode="r") as file:
        yield from csv.reader(file)


def load_s3_files(finder: PathFinder, filter_key: str = None):
    directory = finder.s3_bucket_path
    for file_path in get_s3_full_file_paths(directory, filter_key):
        account = find_account(file_path, finder.schema)

        if not account:
            logger.warning(f"could not parse {file_path}")
            continue

        with get_s3_conn().open(file_path, mode="r") as file:
            df = pandas.read_csv(file, keep_default_na=False)

        yield account, file_path, df


def get_s3_files(directory, filter_key=None):
    for s3_file_name in get_s3_full_file_paths(directory, filter_key):
        body = [row for row in get_s3_rows(s3_file_name)]
        header = body[0]
        rows = body[1:]

        yield s3_file_name, header, rows
