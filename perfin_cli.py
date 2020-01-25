import csv
import logging
import os
import sys
from s3fs.core import S3FileSystem
import subprocess
from perfin.lib.file_matching.analyzer import FileAnalyzer
from perfin.lib.file_matching.util.support import create_file_name, get_account_lookup
from perfin.util.dynamodb_conn import get_user_accounts
from perfin.util.plaid_conn import get_transactions, get_client
from cli.prompts import (
    show_cli_message,
    generate_prompt,
    LIST_DIR_TYPE,
    RENAME_FILES_TYPE,
    UPLOAD_S3_TYPE,
    DELETE_DIR_TYPE,
    RUN_SPIDER_ACTION_TYPE,
    GENERATE_FILE_TYPE
)


logger = logging.getLogger(__file__)


def get_files(directory, file_type):
    for path in os.listdir(directory):
        filename, file_extension = os.path.splitext(path)
        if file_extension.lower() == file_type:
            full_path = '{}/{}'.format(directory, path)
            yield full_path, filename, file_extension


if __name__ == '__main__':
    args = sys.argv

    if len(args) == 4:
        one, two, stage, command = args
    elif len(args) == 3:
        one, two, command = args
    else:
        command = None

    commands = ['shell']
    if command and command in commands:
        if command == 'shell':
            print('Opening {} shell...'.format(ENV))
            time.sleep(2)
            import pdb; pdb.set_trace()

    show_cli_message()

    action_type = generate_prompt(['action_type'])

    if action_type == RENAME_FILES_TYPE:
        report = generate_prompt(['directory'])
        if report == 'custom directory':
            directory = generate_prompt(['custom_directory'])
        else:
            directory = os.path.expanduser(report)

        for old_filename, filename, ext in get_files(directory, '.csv'):
            analyzer = FileAnalyzer(file_path=old_filename)
            reader = analyzer.open_and_yield_csv_row(old_filename)
            header = next(reader, None)
            analyzer = FileAnalyzer(header=header, filename=old_filename)
            new_filename = '{}/{}.csv'.format(directory, analyzer.policy.unique_name)

            print(f'old: {old_filename}')
            print(f'new: {new_filename}')
            os.rename(old_filename, new_filename)
            print('')

    elif action_type == UPLOAD_S3_TYPE:
        s3_path, directory = generate_prompt(['s3_paths', 'directory'])
        directory = os.path.expanduser(directory)
        s3 = S3FileSystem(anon=False)
        if not s3.exists(s3_path):
            raise Exception(f'{s3_path} path does not exist')
        for old_filename, filename, ext in get_files(directory, '.csv'):
            rpath = f'{s3_path}/{filename}.csv'
            s3.put(old_filename, rpath)
            print(old_filename, rpath)
            # os.remove(old_filename)

    elif action_type == DELETE_DIR_TYPE:
        directory = generate_prompt(['directory'])
        directory = os.path.expanduser(directory)
        confirmation = generate_prompt(['confirm'])
        if confirmation:
            for old_filename, filename, ext in get_files(directory, '.csv'):
                os.remove(old_filename)

    elif action_type == LIST_DIR_TYPE:
        directory = generate_prompt(['directory'])
        directory = os.path.expanduser(directory)
        for lpath, filename, ext in get_files(directory, '.csv'):
            print(lpath)

    elif action_type == RUN_SPIDER_ACTION_TYPE:
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
                _file = create_file_name(account.account_name, from_date, to_date)
                _file = '~/Desktop/perfin_files/{}.csv'.format(_file)
                filename = os.path.expanduser(_file)

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

    print('done.')
    print()
