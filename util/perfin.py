import boto3
from .csv_functions import read_classified_file
from .es import get_es_connection, insert_document, create_perfin_index

ES_CONN = get_es_connection()

def local_print_out(event, context):
    for item in get_records(event, aws_fill_none=False):
        print(item)

def get_records(event, aws_fill_none=False):
    records = event["Records"]
    for record in records:
        file_name = record["s3"]["object"]["key"]
        bucket_name = record["s3"]["bucket"]["name"]
        file_url = "%s/%s" % (bucket_name, file_name)    
        for item in read_classified_file(file_url, s3=True):
            yield item 

def lambda_insertion_into_es(event, context):
    index = "perfin_write"
    for item in get_records(event):
        try:
            insert_document(ES_CONN, index, item["_id"], item["document"])
        except:
            print("error: %s" % item)

def local_insertion_all_s3_csvs_into_es(Bucket="mzakany-perfin"):
    s3 = S3FileSystem(anon=False)
    # assumed alias
    index = "perfin_write"
    for full_file_name in s3.ls(path=Bucket):
        for item in read_classified_file(full_file_name, s3=True):
            try:
                insert_document(ES_CONN, index, item["_id"], item["document"])
            except:
                print("problem with: %s" % item)
                pass
                