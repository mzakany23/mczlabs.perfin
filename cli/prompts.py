import os
import sys
import time
import inquirer
import datetime
import pyfiglet
from inquirer.themes import GreenPassion




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


class Prompt:
    @staticmethod
    def directory():
        return inquirer.List('directory',
          message="Choose directory? -> Where perfin files are",
          choices=DIRECTORY_TYPES,
          default=DIRECTORY_TYPES[0]
        )

    @staticmethod
    def custom_directory():
        return inquirer.Text('custom_directory',
          message="Directory path? -> Absolute path where files live",
        )

    @staticmethod
    def date():
        return inquirer.List('date',
          message='Filter by date range?',
          choices=DATE_TYPES,
          default=DATE_TYPES[0]
        )

    @staticmethod
    def platform_types():
        return inquirer.Checkbox('platform_types',
          message='What platforms do you want to export?',
          choices=PLATFORM_TYPEsS,
          default='twitter'
        )

    @staticmethod
    def create_in_new_crowd():
        return inquirer.Confirm('create_in_new_crowd',
          message='Create entity in new crowd?',
          default=False
        )
    @staticmethod
    def report_type():
        return inquirer.List('report_type',
          message='What type of report do you want to do?',
          choices=REPORT_TYPES,
          default=REPORT_TYPES[0]
        )

    @staticmethod
    def env():
        return inquirer.List('env',
          message='What entities do you want to see?',
          choices=ENV_TYPES,
          default=ENV_TYPES[0]
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


RENAME_FILES_TYPE = f"rename_files -> rename all files in directory"

NOW = datetime.datetime.utcnow()
TODAY = NOW.strftime('%m-%d-%Y')

ACTION_TYPES = [
  RENAME_FILES_TYPE,
]

DIRECTORY_TYPES = ['~/Desktop/perfin_files']
DATE_TYPES = ['all'] + last_x_days(5, '%m-%d-%Y')
