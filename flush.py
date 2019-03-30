from util.es import *
from handler import *
from s3fs.core import S3FileSystem



ES_CONN = get_es_connection()


def flush():
    delete_index(ES_CONN, 'transactions')
    create_index(ES_CONN, 'transactions', perfin_schema)


def init():
    s3 = S3FileSystem(anon=False)
    files = s3.ls(path="mzakany-perfin")
    insert_files(files, "transactions_write")

# if __name__ == "__main__":
#     # flush()
#     init()
#     pass