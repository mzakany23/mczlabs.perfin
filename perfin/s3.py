import csv
import logging

import pandas
import s3fs

from .accounts import find_account

S3 = s3fs.S3FileSystem(anon=False)

logger = logging.getLogger(__name__)


def get_s3_full_file_paths(directory: str, filter_key: str = None):
    for s3_file_path in S3.ls(directory):
        if filter_key:
            if filter_key in s3_file_path:
                yield s3_file_path
        else:
            yield s3_file_path


def move_s3_files(bucket: str, original_directory: str, directory: str):
    for s3_file_path in get_s3_full_file_paths(original_directory):
        if directory not in s3_file_path:
            file_name = s3_file_path.split("/")[1]
            full_dir = "{}/{}".format(bucket, directory)
            new_path = "{}/{}".format(full_dir, file_name)
            S3.mv(s3_file_path, new_path)


def get_s3_rows(file_path: str):
    _open = S3.open(file_path, mode="r")
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

        with S3.open(file_path, mode="r") as file:
            df = pandas.read_csv(file, keep_default_na=False)

        yield account, file_path, df


def get_s3_files(directory, filter_key=None):
    for s3_file_name in get_s3_full_file_paths(directory, filter_key):
        body = [row for row in get_s3_rows(s3_file_name)]
        header = body[0]
        rows = body[1:]

        yield s3_file_name, header, rows
