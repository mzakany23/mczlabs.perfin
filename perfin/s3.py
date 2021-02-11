import csv

from s3fs import S3FileSystem

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
