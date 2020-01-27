import datetime
import logging

from datetime import timedelta

from perfin.lib.file_matching.util.support import generate_specific_key
from perfin.util.dynamodb_conn import get_user_accounts
from perfin.util.plaid_conn import get_client, get_transactions

import sentry_sdk

from .lib.file_matching.analyzer import FileAnalyzer
from .settings.base import load_settings
from .util.es.es_conn import get_es_connection, insert_document

ES_CONN = get_es_connection()

logger = logging.getLogger(__name__)

INDEX = load_settings()['INDEX']


def upload_transactions(*args):
    if len(args) == 2:
        event, context = args
    client = get_client()
    fmt = '%Y-%m-%d'
    now = datetime.datetime.utcnow()
    ago = now - timedelta(days=2)
    accounts = get_user_accounts('mzakany')
    from_date = ago.strftime(fmt)
    to_date = now.strftime(fmt)
    es_conn = get_es_connection()
    logger.info('getting accounts')

    for account in accounts:
        if 'capital' not in account.account_name:
            account_name = account.account_name
            account_items = get_transactions(client, account, from_date, to_date)
            logger.info('processing periodic upload of {} {} {}'.format(account_name, from_date, to_date))

            for item in account_items:
                transactions = item['transactions']
                for transaction in transactions:
                    if transaction['pending']:
                        continue

                    amount = transaction['amount']
                    amount *= -1
                    date = transaction['date']
                    description = transaction['name']
                    id_key = '{}{}{}'.format(date, description, amount)
                    document = {
                        "_id" : generate_specific_key(id_key),
                        "document" : {
                            "group" : description[:10],
                            "account" : account_name
                        }
                    }
                    write_alias = '{}_write'.format(INDEX)
                    insert_document(es_conn, write_alias, document["_id"], document)


def process_files(*args):
    if len(args) == 2:
        event, context = args
    try:
        logger.info('writing to es index {}'.format(INDEX))
        records = event["Records"]
        file_paths = []
        for record in records:
            file_name = record["s3"]["object"]["key"]
            bucket_name = record["s3"]["bucket"]["name"]
            file_path = "%s/%s" % (bucket_name, file_name)
            file_paths.append(file_path)

        for file_path in file_paths:
            logger.info('inserting file_path {}'.format(file_path))
            analyzer = FileAnalyzer(file_path=file_path, trim_field='description')
            for row in analyzer.get_rows():
                document = row["document"]
                document["group"] = row["_group"]
                write_alias = '{}_write'.format(INDEX)
                insert_document(ES_CONN, write_alias, row["_id"], document)
    except Exception as e:
        message = str(e)
        logging.exception(message)
        sentry_sdk.capture_message(message)
