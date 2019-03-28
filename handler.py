import os
import sentry_sdk
from s3fs.core import S3FileSystem
from util.csv_functions import read_classified_file, open_and_yield_csv_row
from util.es import get_es_connection, insert_document, create_index, perfin_schema, delete_index


ES_CONN = get_es_connection()

sentry_key = os.environ.get('SENTRY_KEY')

if sentry_key:
    sentry_sdk.init(sentry_key)

S3 = os.environ.get("s3", True)



def insert_files(file_paths, index):
    for file_path in file_paths:
        for row in read_classified_file(file_path, s3=S3):
            document = row["document"]
            document["group"] = row["_group"]
            print(document)
            insert_document(ES_CONN, index, row["_id"], document)


def insert_file(event, context):
    records = event["Records"]
    for record in records:
        file_name = record["s3"]["object"]["key"]
        bucket_name = record["s3"]["bucket"]["name"]
        file_path = "%s/%s" % (bucket_name, file_name)
        index = "transactions_write"
        for row in read_classified_file(file_path, s3=S3):
            document = row["document"]
            document["group"] = row["_group"]
            insert_document(ES_CONN, index, row["_id"], document)


def flush():
    delete_index(ES_CONN, 'transactions')
    create_index(ES_CONN, 'transactions', perfin_schema)


def init():
    s3 = S3FileSystem(anon=False)
    files = s3.ls(path="mzakany-perfin")
    insert_files(files, "transactions_write")


if __name__ == "__main__":
    # flush()
    # init()
    pass
    
    
