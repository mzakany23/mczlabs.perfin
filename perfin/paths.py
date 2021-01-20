import datetime
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import pandas

from .accounts import find_account
from .s3 import load_s3_files
from .settings import config

logger = logging.getLogger(__name__)


@dataclass
class PathFinder:
    csv_path: Path = None
    csv_patterns: List = field(default_factory=lambda: ["*.csv", "*.CSV"])
    s3_bucket_path: str = None

    @property
    def paths(self):
        if self.csv_path:
            for pattern in self.csv_patterns:
                for path in self.csv_path.glob(pattern):
                    yield path

    def load_files(self):
        if self.csv_path:
            return load_files(self)
        elif self.s3_bucket_path:
            return load_s3_files(self.s3_bucket_path)


def load_files(finder: PathFinder):
    for path in finder.paths:
        account = None

        df = pandas.read_csv(f"{path}", keep_default_na=False)

        account = find_account(path.name.lower())

        if not account:
            logger.warning(f"could not match file alias {path.name.lower()}")
            continue
        logger.info(f"found {path.name.lower()}")
        yield account, path, df


def get_sort_key(account):
    fc = account if isinstance(account, list) else account["file_columns"]

    for col in fc:
        if isinstance(col, list):
            return get_sort_key(col)
        if col.get("sort_key"):
            return col
    raise Exception(f"could not find a sort_key attr in {fc}")


def get_file_names(finder: PathFinder, new_file_ext="csv"):
    for account, path, df in finder.load_files():
        sort_key = get_sort_key(account)
        column_name = sort_key["column_name"]
        dates = df[column_name].to_list()
        date_format = sort_key["date_format"]
        account_name = account["account_name"]
        dates.sort(key=lambda date: datetime.datetime.strptime(date, date_format))
        dates = [datetime.datetime.strptime(date, date_format) for date in dates]
        start_date = datetime.datetime.strftime(dates[0], config.date_fmt)
        end_date = datetime.datetime.strftime(dates[-1], config.date_fmt)
        new_file_name = f"{config.create_file_name(account_name, start_date, end_date)}.{new_file_ext}"
        yield path, new_file_name


def move_files(finder: PathFinder):
    for file, new_file_name in get_file_names(finder):
        nfp = config.root_path.joinpath(f"files/{new_file_name}")
        file.rename(nfp)
        logger.info(f"successfully moved {nfp}")
