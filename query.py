from perfin.util.s3_conn import get_s3_processed_docs


if __name__ == '__main__':
    for row in get_s3_processed_docs():
        print(row)