import os
import sentry_sdk
from .util.csv_functions import read_classified_file
from .util.es import get_es_connection, insert_document




ES_CONN = get_es_connection()

sentry_key = os.environ.get('SENTRY_KEY')

if sentry_key:
    sentry_sdk.init(sentry_key)

S3 = os.environ.get("s3", True)


def insert_files(file_paths, index, **kwargs):
    insert_fn = kwargs.get('insert_fn', insert_document)
    read_csv_fn = kwargs.get('read_csv_fn', read_classified_file)
    for file_path in file_paths:
        for row in read_csv_fn(file_path, s3=S3):
            document = row["document"]
            document["group"] = row["_group"]
            insert_fn(ES_CONN, index, row["_id"], document)


def process_files(event, context, **kwargs):
    insert_fn = kwargs.get('insert_fn', insert_document)
    read_csv_fn = kwargs.get('read_csv_fn', read_classified_file)
    records = event["Records"]
    file_paths = []
    for record in records:
        file_name = record["s3"]["object"]["key"]
        bucket_name = record["s3"]["bucket"]["name"]
        file_path = "%s/%s" % (bucket_name, file_name)
        file_paths.append(file_path)
    insert_files(file_paths, 'transactions_write', **kwargs)
