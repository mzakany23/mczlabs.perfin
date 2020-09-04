import csv
import datetime
import logging
import os
import sys

import inquirer
import pyfiglet
from inquirer.themes import GreenPassion
from perfin.lib.file_matching.util.support import (
    create_file_name,
    generate_doc_id,
    get_account_lookup,
)
from perfin.settings.base import load_settings
from perfin.util.dynamodb_conn import get_user_accounts
from perfin.util.es.es_conn import (
    create_index,
    get_es_config,
    get_es_connection,
    insert_all_rows,
    insert_document,
)
from perfin.util.plaid_conn import get_client, get_transactions
from s3fs.core import S3FileSystem

logger = logging.getLogger(__name__)


class Prompt:
    @staticmethod
    def stats_type(*args, **kwargs):
        _types = ["all"]
        return inquirer.List(
            "stats_type",
            message="What type of email to send?",
            choices=_types,
            default=_types[0],
        )

    @staticmethod
    def serverless_fn(*args, **kwargs):
        _types = ["all", "ingest_files", "periodic_ingest"]
        return inquirer.List(
            "serverless_fn",
            message="What fn do you want to deploy?",
            choices=_types,
            default=_types[0],
        )

    @staticmethod
    def local_file_type(*args, **kwargs):
        _types = ["list", "delete"]
        return inquirer.List(
            "local_file_type",
            message="Select local file cmd",
            choices=_types,
            default=_types[0],
        )

    @staticmethod
    def serverless_cmd(*args, **kwargs):
        _types = ["deploy", "remove"]
        return inquirer.List(
            "serverless_cmd",
            message="Select serverless command",
            choices=_types,
            default=_types[0],
        )

    @staticmethod
    def es_type(*args, **kwargs):
        return inquirer.List(
            "es_type",
            message="Select ES Action",
            choices=ES_ACTIONS,
            default=ES_ACTIONS[0],
        )

    @staticmethod
    def username(*args, **kwargs):
        return inquirer.List(
            "username", message="Select a user", choices=USERS, default=USERS[0]
        )

    @staticmethod
    def from_date(*args, **kwargs):
        now = datetime.datetime.now()
        then = now - datetime.timedelta(days=30)

        return inquirer.Text(
            "from_date", message="Enter from date", default=then.strftime("%Y-%m-%d")
        )

    @staticmethod
    def to_date(*args, **kwargs):
        now = datetime.datetime.now()
        return inquirer.Text(
            "to_date", message="Enter to date", default=now.strftime("%Y-%m-%d")
        )

    @staticmethod
    def account_action(*args, **kwargs):
        return inquirer.List(
            "account_action",
            message="Choose action",
            choices=TRANSACTION_TYPES,
            default=TRANSACTION_TYPES[0],
        )

    @staticmethod
    def s3_paths(*args, **kwargs):
        return inquirer.List(
            "s3_paths",
            message="Choose s3 path",
            choices=S3_PATH_TYPES,
            default=S3_PATH_TYPES[0],
        )

    @staticmethod
    def directory(*args, **kwargs):
        return inquirer.List(
            "directory",
            message="Choose directory",
            choices=DIRECTORY_TYPES,
            default=DIRECTORY_TYPES[0],
        )

    @staticmethod
    def confirm(*args, **kwargs):
        return inquirer.Confirm("confirm", message="Are you sure?", default=False)

    @staticmethod
    def custom_directory(*args, **kwargs):
        return inquirer.Text("custom_directory", message="Directory path",)

    @staticmethod
    def date(*args, **kwargs):
        return inquirer.List(
            "date",
            message="Filter by date range",
            choices=DATE_TYPES,
            default=DATE_TYPES[0],
        )

    @staticmethod
    def action_type(*args, **kwargs):
        return inquirer.List(
            "action_type", message="What do you want to do?", choices=ACTION_TYPES
        )

    @staticmethod
    def accounts(*args, **kwargs):
        accounts = args[0]
        choices = [account.account_name for account in accounts]
        return inquirer.Checkbox(
            "accounts", message="Choose account", choices=choices, default=choices[0]
        )


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def show_cli_message():
    env = os.environ.get("PERFIN_ENV", "PROD")
    message = "Perfin CLI {}".format(env)
    ascii_banner = pyfiglet.figlet_format(message)
    print(ascii_banner)


def generate_prompt(prompts, *args, **kwargs):
    prompts = [getattr(Prompt, prompt)(*args, **kwargs) for prompt in prompts]
    report = inquirer.prompt(prompts, theme=GreenPassion())
    if not report:
        raise Exception("user exited prompt before all inputs were given!")
    values = list(report.values())
    if len(values) == 1:
        return values[0]
    return values


def last_x_days(num, fmt):
    now = datetime.datetime.now()
    return [
        datetime.datetime.strftime(now - datetime.timedelta(i), fmt) for i in range(num)
    ]


NOW = datetime.datetime.utcnow()
TODAY = NOW.strftime("%m-%d-%Y")

LOCAL_FILES_TYPE = "local_files -> manage local files"
DOWNLOAD_TRANSACTION_TYPE = "plaid -> download account data"
GENERATE_FILE_TYPE = "generate_csv -> generate a csv"
RESET_ACCOUNT_TYPE = "reset_account -> reset account creds"
UPLOAD_TRANS_TYPE = "upload_transactions -> upload transactions directly"
UPLOAD_S3_TYPE = "s3 -> upload files to s3"
ES_CONN_TYPE = "elasticsearch -> manage elasticsearch"
DEPLOY_TYPE = "serverless -> run a serverless command"
STATS_TYPE = "stats -> send emails of stats"

ACTION_TYPES = [
    LOCAL_FILES_TYPE,
    UPLOAD_S3_TYPE,
    DOWNLOAD_TRANSACTION_TYPE,
    ES_CONN_TYPE,
    DEPLOY_TYPE,
    STATS_TYPE,
]
TRANSACTION_TYPES = [UPLOAD_TRANS_TYPE, GENERATE_FILE_TYPE, RESET_ACCOUNT_TYPE]
ES_ACTIONS = ["recreate_index", "seed_files_from_s3"]
USERS = ["mzakany"]
DIRECTORY_TYPES = ["~/Desktop/perfin_files"]
S3_PATH_TYPES = ["mzakany-perfin"]
DATE_TYPES = ["all"] + last_x_days(5, "%m-%d-%Y")


def get_files(directory, file_type):
    for path in os.listdir(directory):
        filename, file_extension = os.path.splitext(path)
        if file_extension.lower() == file_type:
            full_path = "{}/{}".format(directory, path)
            yield full_path, filename, file_extension


def list_local_files(directory):
    directory = os.path.expanduser(directory)
    for lpath, filename, ext in get_files(directory, ".csv"):
        print(lpath)


if __name__ == "__main__":
    args = sys.argv

    if len(args) == 4:
        one, two, stage, command = args
    elif len(args) == 3:
        one, two, command = args
    else:
        command = None

    show_cli_message()

    action_type = generate_prompt(["action_type"])

    if action_type == DEPLOY_TYPE:
        serverless_cmd = generate_prompt(["serverless_cmd"])
        serverless_fn = None
        if serverless_cmd == "deploy":
            cmd = "deploy"
            serverless_fn = generate_prompt(["serverless_fn"])
        elif serverless_cmd == "remove":
            if serverless_cmd == "remove":
                cmd = "remove"

        confirm = generate_prompt(["confirm"])
        if confirm:
            env = os.environ["PERFIN_ENV"].lower()
            logger.info("deploying {}".format(env))

            if env == "local":
                raise Exception("you can't deploy local to serverless!")

            if cmd == "deploy":
                run_cmd = "AWS_PROFILE=mzakany serverless deploy --stage {}".format(env)
            elif cmd == "remove":
                run_cmd = "AWS_PROFILE=mzakany serverless remove --stage {}".format(env)

            if serverless_fn != "all":
                run_cmd += " --function {}".format(serverless_fn)
            os.system(run_cmd)
    elif action_type == UPLOAD_S3_TYPE:
        s3_path, directory = generate_prompt(["s3_paths", "directory"])
        list_local_files(directory)
        directory = os.path.expanduser(directory)
        s3 = S3FileSystem(anon=False)
        if not s3.exists(s3_path):
            raise Exception("{} path does not exist".format(s3_path))

        confirm = generate_prompt(["confirm"])

        if confirm:
            for old_filename, filename, ext in get_files(directory, ".csv"):
                fn = os.path.basename(old_filename)
                fn_body = fn.split("____")
                account_name, date_range, key = fn_body
                from_date, to_date = date_range[0:10], date_range[11:]
                rpath = "{}/{}.csv".format(s3_path, filename)
                s3.put(old_filename, rpath)
                logger.info({"old_filename": old_filename, "rpath": rpath})
                # os.remove(old_filename)
    elif action_type == ES_CONN_TYPE:
        es_type = generate_prompt(["es_type"])
        if es_type == "recreate_index":
            index = get_es_config()[3]
            logger.info("creating index {}".format(index))
            create_index()
        elif es_type == "seed_files_from_s3":
            index = get_es_config()[3]
            logger.info("seeding index {}".format(index))
            insert_all_rows(index, filter_key=None)
    elif action_type == LOCAL_FILES_TYPE:
        local_file_type = generate_prompt(["local_file_type"])
        if local_file_type == "list":
            directory = generate_prompt(["directory"])
            list_local_files(directory)
        elif local_file_type == "delete":
            directory = generate_prompt(["directory"])
            directory = os.path.expanduser(directory)
            confirmation = generate_prompt(["confirm"])
            if confirmation:
                for old_filename, filename, ext in get_files(directory, ".csv"):
                    os.remove(old_filename)
    elif action_type == STATS_TYPE:
        stats_type = generate_prompt(["stats_type"])
        if stats_type == "all":
            print("todo")
    elif action_type == DOWNLOAD_TRANSACTION_TYPE:
        account_action = generate_prompt(["account_action"])

        if account_action == UPLOAD_TRANS_TYPE:
            username, from_date, to_date = generate_prompt(
                ["username", "from_date", "to_date"]
            )
            _accounts = [account for account in get_user_accounts(username)]
            accounts = generate_prompt(["accounts"], _accounts)
            selected_accounts = [
                account for account in _accounts if account.account_name in accounts
            ]

            ES_CONN = get_es_connection()
            INDEX = load_settings()["INDEX"]
            WRITE_ALIAS = "{}_write".format(INDEX)
            client = get_client()
            for account in selected_accounts:
                account_name = account.account_name
                account_items = get_transactions(client, account, from_date, to_date)
                logger.info(
                    "processing periodic upload of {} {} {}".format(
                        account_name, from_date, to_date
                    )
                )

                for item in account_items:
                    transactions = item["transactions"]
                    for transaction in transactions:
                        if transaction["pending"]:
                            continue

                        amount = transaction["amount"]
                        amount *= -1
                        date = transaction["date"]
                        description = transaction["name"]
                        _id = generate_doc_id(date, description, amount)
                        document = {
                            "group": description[:10],
                            "account": account_name,
                            "date": date,
                            "description": description,
                            "amount": amount,
                        }
                        insert_document(ES_CONN, WRITE_ALIAS, _id, document)
        elif account_action == "reset_account":
            username, from_date, to_date = generate_prompt(
                ["username", "from_date", "to_date"]
            )
            _accounts = [account for account in get_user_accounts(username)]
            accounts = generate_prompt(["accounts"], _accounts)
            selected_accounts = [
                account for account in _accounts if account.account_name in accounts
            ]

            for account in selected_accounts:
                pass
        elif account_action == GENERATE_FILE_TYPE:
            username, from_date, to_date = generate_prompt(
                ["username", "from_date", "to_date"]
            )
            _accounts = [account for account in get_user_accounts(username)]
            accounts = generate_prompt(["accounts"], _accounts)
            selected_accounts = [
                account for account in _accounts if account.account_name in accounts
            ]
            logger.info("running {}".format(accounts))
            client = get_client()
            if not accounts:
                raise Exception("you have to select an account")

            for account in selected_accounts:
                filename = create_file_name(account.account_name, from_date, to_date)
                full_file_path = "~/Desktop/perfin_files/{}.csv".format(filename)
                filename = os.path.expanduser(full_file_path)
                transactions = get_transactions(client, account, from_date, to_date)
                with open(filename, "w+") as file:
                    fieldnames = ["date", "description", "amount"]
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    for trans in transactions:
                        lookup = get_account_lookup(trans["accounts"])
                        transactions = trans["transactions"]

                        for trans in transactions:
                            if trans["pending"]:
                                continue

                            amount = trans["amount"]

                            amount *= -1

                            writer.writerow(
                                {
                                    "date": trans["date"],
                                    "description": trans["name"],
                                    "amount": amount,
                                }
                            )
                logger.info("{} successfully created".format(account.account_name))
