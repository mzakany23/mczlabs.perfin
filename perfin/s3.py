import csv
import logging

import pandas
import s3fs

from .accounts import find_account

S3 = None

logger = logging.getLogger(__name__)


def get_s3_conn():
    global S3
    if S3:
        return S3
    S3 = s3fs.S3FileSystem(anon=False)
    return S3


def get_s3_full_file_paths(directory: str, filter_key: str = None):
    for s3_file_path in get_s3_conn().ls(directory):
        if filter_key:
            if filter_key in s3_file_path:
                yield s3_file_path
        else:
            yield s3_file_path


def get_s3_rows(file_path: str):
    _open = get_s3_conn().open(file_path, mode="r")
    with _open as f:
        rows = csv.reader(f)
        for row in rows:
            yield row


def load_s3_files(directory: str, filter_key: str = None):
    for file_path in get_s3_full_file_paths(directory, filter_key):
        account = find_account(file_path)
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
