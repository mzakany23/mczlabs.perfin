import csv

from perfin.lib.file_matching.util.support import generate_new_file_name

from s3fs.core import S3FileSystem


def get_s3_rows(s3, file_path):
    _open = s3.open(file_path, mode="r")
    with _open as f:
        rows = csv.reader(f)
        for row in rows:
            yield row


def get_s3_perfin_files():
    s3 = S3FileSystem(anon=False)
    for s3_file_name in s3.ls('mzakany-perfin'):
        body = [row for row in get_s3_rows(s3, s3_file_name)]
        header = body[0]
        rows = body[1:]

        yield s3_file_name, header, rows


def rename_s3_files():
    for old_filename, header, rows in get_s3_perfin_files():
        new_file_name, file_key = generate_new_file_name(old_filename, header, rows)
        if new_file_name:
            new_file_name = 'mzakany-perfin/{}.csv'.format(new_file_name)
            s3 = S3FileSystem(anon=False)
            s3.mv(old_filename, new_file_name)
            print(old_filename)
            print(new_file_name)
            print()
