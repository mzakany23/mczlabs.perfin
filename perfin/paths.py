import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

import pandas
from loguru import logger

from .accounts import find_account, get_file_columns
from .csv import convert_date
from .s3 import get_s3_conn, get_s3_full_file_paths
from .settings import DATE_FMT, generate_better_key


@dataclass
class PathFinder:
    csv_path: Path = None
    csv_patterns: List = field(default_factory=lambda: ["*.csv", "*.CSV"])
    schema: Dict = field(default_factory=dict)
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
        load_fn = load_files if self.csv_path else load_s3_files
        return load_fn(self)


def create_file_name(name, from_date, to_date):
    if "/" in from_date:
        from_date = from_date.replace("/", ".")
    if "/" in to_date:
        to_date = to_date.replace("/", ".")
    key = generate_better_key()[0:10]
    return f"{name}____{from_date}--{to_date}____{key}"


def load_s3_files(finder: PathFinder):
    for file_path in get_s3_full_file_paths(finder.s3_bucket_path):
        account = find_account(file_path, finder.schema)

        if not account:
            logger.warning(f"could not parse {file_path}")
            continue

        with get_s3_conn().open(file_path, mode="r") as file:
            df = pandas.read_csv(file, keep_default_na=False)

        yield account, file_path, df


def load_files(finder: PathFinder):
    for path in finder.paths:
        account = None

        df = pandas.read_csv(f"{path}", keep_default_na=False)

        account = find_account(path.name.lower(), finder.schema)

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
        start_date = datetime.datetime.strftime(dates[0], DATE_FMT)
        end_date = datetime.datetime.strftime(dates[-1], DATE_FMT)
        new_file_name = (
            f"{create_file_name(account_name, start_date, end_date)}.{new_file_ext}"
        )
        yield path, new_file_name


def move_files(finder: PathFinder, move_to_dir: Path):
    for file, new_file_name in get_file_names(finder):
        nfp = move_to_dir.joinpath(f"/{new_file_name}")
        file.rename(nfp)
        logger.info(f"successfully moved {nfp}")
