import logging

import os

import sentry_sdk

from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

from .lib.file_matching.analyzer import FileAnalyzer
from .util.es.es_conn import get_es_connection, insert_document
from .util.globals import INDEX

ES_CONN = get_es_connection()

sentry_key = os.environ.get('SENTRY_KEY')

if sentry_key:
    sentry_sdk.init(dsn=sentry_key, debug=True, integrations=[AwsLambdaIntegration()])

logger = logging.getLogger(__file__)


def process_files(event, context, **kwargs):
    try:
        es_conn = kwargs.get('es', ES_CONN)
        records = event["Records"]
        file_paths = []
        for record in records:
            file_name = record["s3"]["object"]["key"]
            bucket_name = record["s3"]["bucket"]["name"]
            file_path = "%s/%s" % (bucket_name, file_name)
            file_paths.append(file_path)

        for file_path in file_paths:
            analyzer = FileAnalyzer(file_path=file_path, trim_field='description')
            for row in analyzer.get_rows():
                document = row["document"]
                document["group"] = row["_group"]
                write_alias = '{}_write'.format(INDEX)
                insert_document(es_conn, write_alias, row["_id"], document)
    except Exception as e:
        message = str(e)
        logging.exception(message)
        sentry_sdk.capture_message(message)
