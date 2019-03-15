from s3fs.core import S3FileSystem
from .config import TRANSACTION_TYPES, get_account_types
from .classes import RowFactory
from .support import generate_specific_key, strip_white


def to_csv_row(row):
    return (row.decode('utf-8')
        .replace('"', "")
        .replace("\n", "")
        .replace("\r", "")
        .replace("\r\n", "")
        .split(","))

def open_and_yield_csv_row(file_url, **kwargs):
    s3 = kwargs.get("s3")

    if s3:
        s3 = S3FileSystem(anon=False)
        _open = s3.open(file_url, mode='rb')
    else:
        _open = open(file_url, mode='rb')

    with _open as f:
        for row in f.readlines():
            yield to_csv_row(row)

def read_classified_file(file_url, account_types, **kwargs):
    # here! this function will yield you processed rows
    # to insert
    reader = open_and_yield_csv_row(file_url, **kwargs)
    header = next(reader, None)
    account_types = get_account_types()
    header_key = strip_white(str(header))
    if header_key in account_types:
        account = account_types[header_key]
        keys = TRANSACTION_TYPES.keys()
        for row in reader:
            _key_str = ",".join(row).replace(",", "").replace(" ", "")
            _unique_key = generate_specific_key(_key_str)
            row_object = RowFactory(_unique_key, account_types, header_key, row)
            yield row_object.get_doc()
