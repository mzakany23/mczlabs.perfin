import os
from s3fs.core import S3FileSystem
from util.csv_functions import read_classified_file, open_and_yield_csv_row
from util.config import get_account_types
from itertools import groupby
from util.es import get_es_connection, insert_document, create_index, perfin_schema


ES_CONN = get_es_connection()

S3 = os.environ.get("s3", True)


def insert_files(file_paths, index):
    for file_path in file_paths:
        for row in read_classified_file(file_path, s3=S3):
            document = row["document"]
            document["group"] = row["_group"]
            print(document)
            # insert_document(ES_CONN, index, row["_id"], document)


def insert_file(event, context):
    records = event["Records"]
    for record in records:
        file_name = record["s3"]["object"]["key"]
        bucket_name = record["s3"]["bucket"]["name"]
        file_path = "%s/%s" % (bucket_name, file_name)
        for row in read_classified_file(file_path, ACCOUNTS, s3=S3):
            document = row["document"]
            document["group"] = row["_group"]
            insert_document(ES_CONN, "transactions_write", row["_id"], document)


if __name__ == "__main__":
    # create_index(ES_CONN, 'transactions', perfin_schema)

    # files = [
    #     "/Users/mzakany/Desktop/perfin_test_files/Chase4975_Activity_20181202.CSV",
    #     "/Users/mzakany/Desktop/perfin_test_files/2018-12-02_transaction_download.csv",
    #     "/Users/mzakany/Desktop/perfin_test_files/2018-12-02_transaction_download (3).csv",
    #     "/Users/mzakany/Desktop/perfin_test_files/2018-12-02_transaction_download (1).csv",
    #     "/Users/mzakany/Desktop/perfin_test_files/2018-12-02_transaction_download (2).csv",
    # ]

    # s3 = S3FileSystem(anon=False)
    # _dir = "/Users/mzakany/Desktop/perfin_test_files"
    # local_files = ["%s/%s" % (_dir, file) for file in os.listdir(_dir) if not file.startswith('.')]

    # insert_files(files)

    s3 = S3FileSystem(anon=False)
    files = s3.ls(path="mzakany-perfin")
    insert_files(files, "transactions_write")

    # s3_files = s3.ls(path='mzakany-perfin')
    # print(local_files)
    # insert_files(s3_files)
