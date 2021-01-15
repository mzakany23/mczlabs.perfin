import csv

import s3fs

S3 = s3fs.S3FileSystem(anon=False)


def get_s3_full_file_paths(directory, filter_key=None):
    for s3_file_path in S3.ls(directory):
        if filter_key:
            if filter_key in s3_file_path:
                yield s3_file_path
        else:
            yield s3_file_path


def move_files_to_dir(bucket, original_directory, directory):
    for s3_file_path in get_s3_full_file_paths(original_directory):
        if directory not in s3_file_path:
            file_name = s3_file_path.split("/")[1]
            full_dir = "{}/{}".format(bucket, directory)
            new_path = "{}/{}".format(full_dir, file_name)
            S3.mv(s3_file_path, new_path)


def get_s3_rows(file_path):
    _open = S3.open(file_path, mode="r")
    with _open as f:
        rows = csv.reader(f)
        for row in rows:
            yield row


def get_s3_perfin_files(directory, filter_key=None):
    for s3_file_name in get_s3_full_file_paths(directory, filter_key):
        body = [row for row in get_s3_rows(s3_file_name)]
        header = body[0]
        rows = body[1:]

        yield s3_file_name, header, rows
