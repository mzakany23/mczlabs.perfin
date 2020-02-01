"""This is the main handler file that contains all the perfin lambda functions."""
import csv
import logging
import tempfile

from perfin.util.dynamodb_conn import get_user_accounts
from perfin.util.plaid_conn import get_client, get_transactions

from .lib.file_matching.util.support import create_file_name, get_date_range, generate_doc_id
from .lib.file_matching.analyzer import FileAnalyzer
from .settings.base import load_settings
from .util.es.es_conn import get_es_connection, insert_document

from s3fs.core import S3FileSystem

LOOKBACK_DAYS = 10
ES_CONN = get_es_connection()
INDEX = load_settings()['INDEX']
WRITE_ALIAS = '{}_write'.format(INDEX)

logger = logging.getLogger(__name__)


def upload_files(*args):
    """Upload files to s3."""
    logger.info('getting accounts')
    accounts = get_user_accounts('mzakany', exclude=['capital'])
    from_date, to_date = get_date_range(LOOKBACK_DAYS)
    client = get_client()
    for account in accounts:
        filename = create_file_name(account.account_name, from_date, to_date)
        rpath = '{}/{}.csv'.format('mzakany-perfin', filename)
        transactions = get_transactions(client, account, from_date, to_date)
        local_file = tempfile.NamedTemporaryFile(mode='w+')
        with local_file as file:

            fieldnames = ['date', 'description', 'amount']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for trans in transactions:
                transactions = trans['transactions']

                for trans in transactions:
                    if trans['pending']:
                        continue

                    amount = trans['amount']

                    amount *= -1

                    writer.writerow({
                        'date': trans['date'],
                        'description': trans['name'],
                        'amount': amount
                    })
            file.seek(0)
            s3 = S3FileSystem(anon=False)
            s3.put(local_file.name, rpath)


def upload_transactions(*args):
    """Plaid upload to es."""
    client = get_client()
    from_date, to_date = get_date_range(LOOKBACK_DAYS)
    accounts = get_user_accounts('mzakany', exclude=['capital'])
    logger.info('getting accounts')

    for account in accounts:
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
    """S3 event listener."""
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
