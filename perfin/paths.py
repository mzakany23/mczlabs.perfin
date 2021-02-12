from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Tuple

from loguru import logger
from pandas import DataFrame

from .settings import DATE_FMT
from .util import convert_date, create_file_name


@dataclass
class LocalCSVFileFinder:
    base_path: str = "~/Desktop"
    patterns: List = field(default_factory=lambda: ["*.csv", "*.CSV"])

    def get_paths(self) -> Path:
        path = Path(self.base_path).expanduser()

        if path.is_file():
            yield path
        else:
            for pattern in self.patterns:
                yield from path.glob(pattern)

    def load_files(self):
        for path in self.get_paths():
            yield path


@dataclass
class S3CSVFileFinder:
    base_path: str
    patterns: List = field(default_factory=lambda: ["*.csv", "*.CSV"])

    def move(self, file: Path):
        pass

    def load_files(self):
        pass


def get_files(finder: Callable, new_file_ext="csv"):
    for account, path, df in finder.load_files():
        _, sort_key = get_file_columns(df, account)
        column_name = sort_key["column_name"]
        dates = df[column_name].to_list()
        if not dates:
            logger.warning(f"found {path.name} but is blank, so skipping...")
            continue
        date_format = sort_key["date_format"]
        config_key = account["config_key"]
        dates = [convert_date(date, date_format) for date in dates]
        dates.sort()
        start_date = datetime.strftime(dates[0], DATE_FMT)
        end_date = datetime.strftime(dates[-1], DATE_FMT)
        new_file_name = (
            f"{create_file_name(config_key, start_date, end_date)}.{new_file_ext}"
        )
        yield path, new_file_name


def move_files(finder: Callable, move_to_dir: Path):
    for file, new_file_name in get_files(finder):
        nfp = move_to_dir.joinpath(f"/{new_file_name}")
        file.rename(nfp)
        logger.info(f"successfully moved {nfp}")


def get_file_columns(df: DataFrame, config_meta: Dict) -> Tuple[List, str]:
    file_column_groups = config_meta["file_columns"]

    if isinstance(file_column_groups[0], dict):
        file_column_groups = [file_column_groups]

    df_cols = None

    for file_columns in file_column_groups:
        try:
            df_cols = df.columns

            assert len(df_cols) == len(file_columns)

            for i, col in enumerate(file_columns):
                if isinstance(col["column_name"], list):
                    inner_col = col["column_name"]
                    inner_col_len = len(inner_col) - 1
                    for _, icol in enumerate(inner_col):
                        if df_cols[i].lower() == icol.lower():
                            col["column_name"] = icol
                            break
                        if i == inner_col_len:
                            raise AssertionError(
                                f"{df_cols[i].lower()} == {icol.lower()}"
                            )
                else:
                    assert df_cols[i].lower() == col["column_name"].lower()
        except AssertionError as e:
            logger.warning(e)
            continue
        return file_columns, get_sort_key(file_columns)

    inspect_cols = ""

    for col in file_column_groups:
        inner_col = []
        for inner in col:
            inner_col.append(inner["column_name"])
        inspect_cols += f"\ncolumn: {inner_col}\n"

    raise Exception(f"Could not match {file_column_groups} with {df_cols}")


def find_config(search_name: str, schema: Dict):
    for config_key, config in schema.items():
        for account_alias in config["file_name_search"]:
            alias_match = account_alias.lower() in search_name.lower()
            if alias_match:
                config["config_key"] = config_key
                return config
    raise Exception(f"Could not match {search_name}")


def get_sort_key(file_columns: List):
    for col in file_columns:
        if isinstance(col, list):
            return get_sort_key(col)
        if col.get("sort_key"):
            return col
    raise Exception(f"could not find a sort_key attr in {file_columns}")
