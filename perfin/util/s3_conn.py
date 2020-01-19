import csv

from perfin.lib.file_matching.analyzer import FileAnalyzer
from perfin.lib.file_matching.util.support import generate_new_file_name

from s3fs.core import S3FileSystem


S3 = S3FileSystem(anon=False)


def s3_move(old_filename, new_file_name):
    S3.mv(old_filename, new_file_name)


def move_files_to_dir(original_directory, directory):
    for s3_file_path in get_s3_full_file_paths(original_directory):
        if directory not in s3_file_path:
            file_name = s3_file_path.split('/')[1]
            full_dir = 'mzakany-perfin/{}'.format(directory)
            new_path = '{}/{}'.format(full_dir, file_name)
            s3_move(s3_file_path, new_path)


def get_s3_rows(file_path):
    _open = S3.open(file_path, mode="r")
    with _open as f:
        rows = csv.reader(f)
        for row in rows:
            yield row


def get_s3_full_file_paths(directory, filter_key=None):
    for s3_file_path in S3.ls(directory):
        if filter_key:
            if filter_key in s3_file_path:
                yield s3_file_path
        else:
            yield s3_file_path


def get_s3_perfin_files(directory, filter_key=None):
    for s3_file_name in get_s3_full_file_paths(directory, filter_key):
        body = [row for row in get_s3_rows(s3_file_name)]
        header = body[0]
        rows = body[1:]

        yield s3_file_name, header, rows


def rename_s3_files(directory):
    for old_filename, header, rows in get_s3_perfin_files(directory):
        new_file_name, file_key = generate_new_file_name(old_filename, header, rows)
        if new_file_name:
            new_file_name = '{}/{}.csv'.format(directory, new_file_name)
            s3_move(old_filename, new_file_name)
            print(old_filename)
            print(new_file_name)
            print()


def get_s3_processed_docs(directory, filter_key=None):
    for s3_file_name, header, rows in get_s3_perfin_files(directory, filter_key):
        if '__' not in s3_file_name:
            continue
        analyzer = FileAnalyzer(s3_file_name, header, rows, trim_field='description')
        for row in analyzer.get_rows():
            yield row
