import os
import sys
import time
import inquirer
import datetime
import pyfiglet
from inquirer.themes import GreenPassion

from perfin.util.dynamodb_conn import get_user_accounts


class Prompt:
    @staticmethod
    def stats_type(*args, **kwargs):
        _types = ['all']
        return inquirer.List('stats_type',
          message="What type of email to send?",
          choices=_types,
          default=_types[0]
        )

    @staticmethod
    def serverless_fn(*args, **kwargs):
        _types = ['all', 'ingest_files', 'periodic_ingest']
        return inquirer.List('serverless_fn',
          message="What fn do you want to deploy?",
          choices=_types,
          default=_types[0]
        )

    @staticmethod
    def local_file_type(*args, **kwargs):
        _types = ['list', 'delete']
        return inquirer.List('local_file_type',
          message="Select local file cmd",
          choices=_types,
          default=_types[0]
        )

    @staticmethod
    def serverless_cmd(*args, **kwargs):
        _types = ['deploy', 'remove']
        return inquirer.List('serverless_cmd',
          message="Select serverless command",
          choices=_types,
          default=_types[0]
        )

    @staticmethod
    def es_type(*args, **kwargs):
        return inquirer.List('es_type',
          message="Select ES Action",
          choices=ES_ACTIONS,
          default=ES_ACTIONS[0]
        )

    @staticmethod
    def username(*args, **kwargs):
        return inquirer.List('username',
          message="Select a user",
          choices=USERS,
          default=USERS[0]
        )

    @staticmethod
    def from_date(*args, **kwargs):
        now = datetime.datetime.now()
        then = (now - datetime.timedelta(days=30))

        return inquirer.Text('from_date',
          message="Enter from date",
          default=then.strftime('%Y-%m-%d')
        )

    @staticmethod
    def to_date(*args, **kwargs):
        now = datetime.datetime.now()
        return inquirer.Text('to_date',
          message="Enter to date",
          default=now.strftime('%Y-%m-%d')
        )

    @staticmethod
    def account_action(*args, **kwargs):
        return inquirer.List('account_action',
          message="Choose action",
          choices=TRANSACTION_TYPES,
          default=TRANSACTION_TYPES[0]
        )

    @staticmethod
    def s3_paths(*args, **kwargs):
        return inquirer.List('s3_paths',
          message="Choose s3 path",
          choices=S3_PATH_TYPES,
          default=S3_PATH_TYPES[0]
        )
    @staticmethod
    def directory(*args, **kwargs):
        return inquirer.List('directory',
          message="Choose directory",
          choices=DIRECTORY_TYPES,
          default=DIRECTORY_TYPES[0]
        )

    @staticmethod
    def confirm(*args, **kwargs):
        return inquirer.Confirm('confirm',
          message="Are you sure?",
          default=False
        )
    @staticmethod
    def custom_directory(*args, **kwargs):
        return inquirer.Text('custom_directory',
          message="Directory path",
        )

    @staticmethod
    def date(*args, **kwargs):
        return inquirer.List('date',
          message='Filter by date range',
          choices=DATE_TYPES,
          default=DATE_TYPES[0]
        )
    @staticmethod
    def action_type(*args, **kwargs):
        return inquirer.List('action_type',
          message='What do you want to do?',
          choices=ACTION_TYPES
        )

    @staticmethod
    def accounts(*args, **kwargs):
        accounts = args[0]
        choices = [account.account_name for account in accounts]
        return inquirer.Checkbox('accounts',
          message="Choose account",
          choices=choices,
          default=choices[0]
        )


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def show_cli_message():
    env = os.environ.get('PERFIN_ENV', 'PROD')
    message = 'Perfin CLI {}'.format(env)
    ascii_banner = pyfiglet.figlet_format(message)
    print(ascii_banner)


def generate_prompt(prompts, *args, **kwargs):
    prompts = [getattr(Prompt, prompt)(*args, **kwargs) for prompt in prompts]
    report = inquirer.prompt(prompts, theme=GreenPassion())
    if not report:
        raise Exception('user exited prompt before all inputs were given!')
    values = list(report.values())
    if len(values) == 1:
        return values[0]
    return values


def last_x_days(num, fmt):
    now = datetime.datetime.now()
    return [datetime.datetime.strftime(now - datetime.timedelta(i), fmt) for i in range(num)]

NOW = datetime.datetime.utcnow()
TODAY = NOW.strftime('%m-%d-%Y')

LOCAL_FILES_TYPE = "local_files -> manage local files"
DOWNLOAD_TRANSACTION_TYPE = "plaid -> download account data"
GENERATE_FILE_TYPE = 'generate_csv -> generate a csv'
UPLOAD_S3_TYPE = "s3 -> upload files to s3"
ES_CONN_TYPE = 'elasticsearch -> manage elasticsearch'
DEPLOY_TYPE = 'serverless -> run a serverless command'
STATS_TYPE = 'stats -> send emails of stats'

ACTION_TYPES = [
  LOCAL_FILES_TYPE,
  UPLOAD_S3_TYPE,
  DOWNLOAD_TRANSACTION_TYPE,
  ES_CONN_TYPE,
  DEPLOY_TYPE,
  STATS_TYPE
]
TRANSACTION_TYPES = [GENERATE_FILE_TYPE]
ES_ACTIONS = ['recreate_index', 'seed_files_from_s3']
USERS = ['mzakany']
DIRECTORY_TYPES = ['~/Desktop/perfin_files']
S3_PATH_TYPES = ['mzakany-perfin']
DATE_TYPES = ['all'] + last_x_days(5, '%m-%d-%Y')
