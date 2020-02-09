import csv
import logging
import os
import sys

from cli.prompts import (
    DEPLOY_TYPE,
    DOWNLOAD_TRANSACTION_TYPE,
    ES_CONN_TYPE,
    GENERATE_FILE_TYPE,
    LOCAL_FILES_TYPE,
    STATS_TYPE,
    UPLOAD_S3_TYPE,
    generate_prompt,
    show_cli_message,
)

from perfin.lib.file_matching.util.support import create_file_name, get_account_lookup
from perfin.util.dynamodb_conn import get_user_accounts
from perfin.util.es.es_conn import create_index, get_es_config, insert_all_rows

from perfin.util.plaid_conn import get_client, get_transactions

from s3fs.core import S3FileSystem


logger = logging.getLogger(__name__)


def get_files(directory, file_type):
    for path in os.listdir(directory):
        filename, file_extension = os.path.splitext(path)
        if file_extension.lower() == file_type:
            full_path = '{}/{}'.format(directory, path)
            yield full_path, filename, file_extension


def list_local_files(directory):
    directory = os.path.expanduser(directory)
    for lpath, filename, ext in get_files(directory, '.csv'):
        print(lpath)


if __name__ == '__main__':
    args = sys.argv

    if len(args) == 4:
        one, two, stage, command = args
    elif len(args) == 3:
        one, two, command = args
    else:
        command = None

    show_cli_message()

    action_type = generate_prompt(['action_type'])

    if action_type == DEPLOY_TYPE:
        serverless_cmd = generate_prompt(['serverless_cmd'])
        serverless_fn = None
        if serverless_cmd == 'deploy':
            cmd = 'deploy'
            serverless_fn = generate_prompt(['serverless_fn'])
        elif serverless_cmd == 'remove':
            if serverless_cmd == 'remove':
                cmd = 'remove'

        confirm = generate_prompt(['confirm'])
        if confirm:
            env = os.environ['PERFIN_ENV'].lower()
            logger.info('deploying {}'.format(env))

            if env == 'local':
                raise Exception("you can't deploy local to serverless!")

            if cmd == 'deploy':
                run_cmd = 'AWS_PROFILE=mzakany serverless deploy --stage {}'.format(env)
            elif cmd == 'remove':
                run_cmd = 'AWS_PROFILE=mzakany serverless remove --stage {}'.format(env)

            if serverless_fn is not 'all':
                run_cmd += ' --function {}'.format(serverless_fn)
            os.system(run_cmd)
    elif action_type == UPLOAD_S3_TYPE:
        s3_path, directory = generate_prompt(['s3_paths', 'directory'])
        list_local_files(directory)
        directory = os.path.expanduser(directory)
        s3 = S3FileSystem(anon=False)
        if not s3.exists(s3_path):
            raise Exception('{} path does not exist'.format(s3_path))

        confirm = generate_prompt(['confirm'])

        if confirm:
            for old_filename, filename, ext in get_files(directory, '.csv'):
                fn = os.path.basename(old_filename)
                fn_body = fn.split('____')
                account_name, date_range, key = fn_body
                from_date, to_date = date_range[0:10], date_range[11:]
                rpath = '{}/{}.csv'.format(s3_path, filename)
                s3.put(old_filename, rpath)
                logger.info({
                    'old_filename' : old_filename,
                    'rpath' : rpath
                })
                # os.remove(old_filename)
    elif action_type == ES_CONN_TYPE:
        es_type = generate_prompt(['es_type'])
        if es_type == 'recreate_index':
            index = get_es_config()[3]
            logger.info('creating index {}'.format(index))
            create_index()
        elif es_type == 'seed_files_from_s3':
            index = get_es_config()[3]
            logger.info('seeding index {}'.format(index))
            insert_all_rows(index, filter_key=None)
    elif action_type == LOCAL_FILES_TYPE:
        local_file_type = generate_prompt(['local_file_type'])
        if local_file_type == 'list':
            directory = generate_prompt(['directory'])
            list_local_files(directory)
        elif local_file_type == 'delete':
            directory = generate_prompt(['directory'])
            directory = os.path.expanduser(directory)
            confirmation = generate_prompt(['confirm'])
            if confirmation:
                for old_filename, filename, ext in get_files(directory, '.csv'):
                    os.remove(old_filename)
    elif action_type == STATS_TYPE:
        stats_type = generate_prompt(['stats_type'])
        if stats_type == 'all':
            print('todo')
    elif action_type == DOWNLOAD_TRANSACTION_TYPE:
        account_action = generate_prompt(['account_action'])
        if account_action == GENERATE_FILE_TYPE:
            username, from_date, to_date = generate_prompt(['username', 'from_date', 'to_date'])
            _accounts = [account for account in get_user_accounts(username)]
            accounts = generate_prompt(['accounts'], _accounts)
            selected_accounts = [account for account in _accounts if account.account_name in accounts]
            logger.info('running {}'.format(accounts))
            client = get_client()
            if not accounts:
                raise Exception('you have to select an account')

            for account in selected_accounts:
                filename = create_file_name(account.account_name, from_date, to_date)
                full_file_path = '~/Desktop/perfin_files/{}.csv'.format(filename)
                filename = os.path.expanduser(full_file_path)
                transactions = get_transactions(client, account, from_date, to_date)
                with open(filename, 'w+') as file:
                    fieldnames = ['date', 'description', 'amount']
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    for trans in transactions:
                        lookup = get_account_lookup(trans['accounts'])
                        transactions = trans['transactions']

                        for trans in transactions:
                            if trans['pending']:
                                continue

                            amount = trans['amount']

                            amount *= -1

                            writer.writerow(
                                {
                                    'date': trans['date'],
                                    'description': trans['name'],
                                    'amount': amount
                                }
                            )
                logger.info('{} successfully created'.format(account.account_name))
