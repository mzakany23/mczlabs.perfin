"""This is the main handler file that contains all the perfin lambda functions."""

import logging
import datetime
from datetime import timedelta

from perfin.lib.file_matching.util.support import generate_doc_id
from perfin.util.dynamodb_conn import get_user_accounts
from perfin.util.plaid_conn import get_client, get_transactions

from .lib.file_matching.analyzer import FileAnalyzer
from .settings.base import configure_app, load_settings
from .util.es.es_conn import get_es_connection, insert_document


ES_CONN = get_es_connection()
INDEX = load_settings()['INDEX']
WRITE_ALIAS = '{}_write'.format(INDEX)

logger = logging.getLogger(__name__)


def upload_transactions(*args):
    """Process periodic uploads."""
    if len(args) == 2:
        event, context = args
    client = get_client()
    fmt = '%Y-%m-%d'
    now = datetime.datetime.utcnow()
    ago = now - timedelta(days=2)
    accounts = get_user_accounts('mzakany')
    from_date = ago.strftime(fmt)
    to_date = now.strftime(fmt)
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
                    _id = generate_doc_id(date, description, amount)
                    document = {
                        "group" : description[:10],
                        "account" : account_name,
                        "date" : date,
                        "description" : description,
                        "amount" : amount
                    }
                    insert_document(ES_CONN, WRITE_ALIAS, _id, document)


def process_files(*args):
    """Process file uploads."""
    if len(args) == 2:
        event, context = args

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
            insert_document(ES_CONN, WRITE_ALIAS, row["_id"], document)
