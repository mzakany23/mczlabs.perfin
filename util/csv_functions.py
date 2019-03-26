import csv
from s3fs.core import S3FileSystem
from lib.file_matching.analyzer import FileAnalyzer


def open_and_yield_csv_row(file_url, **kwargs):
    s3 = kwargs.get("s3")

    if s3:
        s3 = S3FileSystem(anon=False)
        _open = s3.open(file_url, mode="r")
    else:
        _open = open(file_url, mode="r")

    with _open as f:
        rows = csv.reader(f)
        for row in rows:
            yield row


def read_classified_file(file_url, **kwargs):
    reader = open_and_yield_csv_row(file_url, **kwargs)
    header = next(reader, None)
    analyzer = FileAnalyzer(header=header, filename=file_url)
    for row in reader:
        yield analyzer.get_doc(row)
        