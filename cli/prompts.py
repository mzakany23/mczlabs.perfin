import os
import sys
import time
import inquirer
import datetime
import pyfiglet
from inquirer.themes import GreenPassion
from perfin.settings.base import ACCOUNT_LOOKUP


class Prompt:
    @staticmethod
    def from_date():
        now = datetime.datetime.now() 
        then = (now - datetime.timedelta(days=30))

        return inquirer.Text('from_date',
          message="Enter from date",
          default=then.strftime('%Y-%m-%d')
        )
    
    @staticmethod
    def to_date():
        now = datetime.datetime.now() 
    
        return inquirer.Text('to_date',
          message="Enter to date",
          default=now.strftime('%Y-%m-%d')
        )

    @staticmethod
    def account_action():
        return inquirer.List('account_action',
          message="Choose action",
          choices=SPIDER_ACTION_TYPES,
          default=SPIDER_ACTION_TYPES[0]
        )

    @staticmethod
    def accounts():
        return inquirer.Checkbox('accounts',
          message="Choose an account",
          choices=SPIDER_ACCOUNT_TYPES,
          default=SPIDER_ACCOUNT_TYPES[0]
        )

    @staticmethod
    def s3_paths():
        return inquirer.List('s3_paths',
          message="Choose s3 path",
          choices=S3_PATH_TYPES,
          default=S3_PATH_TYPES[0]
        )
    @staticmethod
    def directory():
        return inquirer.List('directory',
          message="Choose directory",
          choices=DIRECTORY_TYPES,
          default=DIRECTORY_TYPES[0]
        )

    @staticmethod
    def confirm():
        return inquirer.Confirm('confirm',
          message="Are you sure?",
          default=False
        )
    @staticmethod
    def custom_directory():
        return inquirer.Text('custom_directory',
          message="Directory path",
        )

    @staticmethod
    def date():
        return inquirer.List('date',
          message='Filter by date range',
          choices=DATE_TYPES,
          default=DATE_TYPES[0]
        )    
    @staticmethod
    def action_type():
        return inquirer.List('action_type',
          message='What do you want to do?',
          choices=ACTION_TYPES
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
    message = 'Perfin CLI'
    ascii_banner = pyfiglet.figlet_format(message)
    print(ascii_banner)


def generate_prompt(prompts):
    prompts = [getattr(Prompt, prompt)() for prompt in prompts]
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

    
RENAME_FILES_TYPE = f"rename_files -> rename all files in directory"
UPLOAD_S3_TYPE = f"upload_s3 -> upload your files to s3 directory"
DELETE_DIR_TYPE = f"delete_files -> delete files from local file directory"
LIST_DIR_TYPE = f"list_files -> list files from local file directory"
RUN_SPIDER_ACTION_TYPE = f"download_account_data -> use plaid api"
GENERATE_FILE_TYPE = 'generate csv'

ACTION_TYPES = [
  LIST_DIR_TYPE,
  UPLOAD_S3_TYPE,
  # RENAME_FILES_TYPE,
  DELETE_DIR_TYPE,
  RUN_SPIDER_ACTION_TYPE
]

SPIDER_ACTION_TYPES = [
  GENERATE_FILE_TYPE
]

DIRECTORY_TYPES = ['~/Desktop/perfin_files']
S3_PATH_TYPES = ['mzakany-perfin']
SPIDER_ACCOUNT_TYPES = list(ACCOUNT_LOOKUP.keys())
DATE_TYPES = ['all'] + last_x_days(5, '%m-%d-%Y')
