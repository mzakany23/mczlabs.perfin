import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import pandas
from loguru import logger

from .accounts import find_account, get_file_columns
from .csv import convert_date
from .s3 import load_s3_files
from .settings import config


@dataclass
class PathFinder:
    csv_path: Path = None
    csv_patterns: List = field(default_factory=lambda: ["*.csv", "*.CSV"])
    s3_bucket_path: str = None

    @property
    def paths(self):
        if self.csv_path.is_dir():
            for pattern in self.csv_patterns:
                yield from self.csv_path.glob(pattern)
        elif self.csv_path.is_file():
            suffix = self.csv_path.suffix
            for pattern in self.csv_patterns:
                if suffix in pattern:
                    yield self.csv_path
        else:
            raise Exception(
                f"could not discern {self.csv_path} from {self.csv_patterns}"
            )

    def load_files(self):
        if self.csv_path:
            return load_files(self)
        if self.s3_bucket_path:
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


def get_file_names(finder: PathFinder, new_file_ext="csv"):
    for account, path, df in finder.load_files():
        _, sort_key = get_file_columns(df, account)
        column_name = sort_key["column_name"]
        dates = df[column_name].to_list()
        if not dates:
            logger.warning(f"found {path.name} but is blank, so skipping...")
            continue
        date_format = sort_key["date_format"]
        account_name = account["account_name"]
        dates = [convert_date(date, date_format) for date in dates]
        dates.sort()
        start_date = datetime.datetime.strftime(dates[0], config.date_fmt)
        end_date = datetime.datetime.strftime(dates[-1], config.date_fmt)
        new_file_name = f"{config.create_file_name(account_name, start_date, end_date)}.{new_file_ext}"
        yield path, new_file_name


def move_files(finder: PathFinder):
    for file, new_file_name in get_file_names(finder):
        nfp = config.root_path.joinpath(f"files/{new_file_name}")
        file.rename(nfp)
        logger.info(f"successfully moved {nfp}")
