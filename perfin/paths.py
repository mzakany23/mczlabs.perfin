import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

import boto3
import pandas as pd

from .types import FileColumns

S3 = None


def get_s3_conn():
    global S3
    return S3 if S3 else boto3.client("s3")


@dataclass
class CSVFile:
    file: Any
    path: Any = None


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

    def load_files(self) -> CSVFile:
        for path in self.get_paths():
            yield CSVFile(path, str(path))

    def move(self, file, new_path):
        new_path = new_path.joinpath(file.name)
        file.rename(new_path)


@dataclass
class S3CSVFileFinder:
    base_path: str
    patterns: List = field(default_factory=lambda: ["*.csv", "*.CSV"])

    def load_files(self) -> CSVFile:
        s3 = get_s3_conn()
        res = s3.list_objects_v2(Bucket=self.base_path)
        for content in res["Contents"]:
            file_path = content["Key"]
            if not file_path.lower().endswith(".csv"):
                continue

            with tempfile.NamedTemporaryFile() as file:
                res = get_s3_conn().get_object(Bucket=self.base_path, Key=file_path)
                body = res["Body"].read()
                file.write(body)
                file.seek(0)
                yield CSVFile(file, file_path)

    def move(self, file: Path):
        self.get_s3_conn().put_object(Bucket=self.base_path, Body=file, Key=file.name)


def ensure_dir(path: str) -> Path:
    dir = Path(path)
    dir.mkdir(exist_ok=True, parents=True)
    return dir


def get_file_columns(df: pd.DataFrame, config_meta: Dict) -> FileColumns:
    file_column_groups = config_meta["file_columns"]

    if isinstance(file_column_groups[0], dict):
        file_column_groups = [file_column_groups]

    df_cols = None

    for file_columns in file_column_groups:
        df_cols = df.columns

        # try and match a different column on fail
        if not len(df_cols) == len(file_columns):
            continue

        for i, col in enumerate(file_columns):
            # in this instance, column_name in the json format
            # object is a list, so checking multiple values
            if isinstance(col["column_name"], list):
                inner_col = col["column_name"]
                for icol in inner_col:
                    if df_cols[i].lower() == icol.lower():
                        col["column_name"] = icol
                        break
                else:
                    raise AssertionError()
            # in this instance is only a string
            else:
                if not df_cols[i].lower() == col["column_name"].lower():
                    raise AssertionError()

        return file_columns, get_sort_key(file_columns)
    else:
        return None, None


def find_config(search_name: str, schema: Dict) -> Dict:
    for config_key, config in schema.items():
        for account_alias in config["file_name_search"]:
            alias_match = account_alias.lower() in search_name.lower()
            if alias_match:
                config["config_key"] = config_key
                return config
    raise Exception(f"Could not match {search_name}")


def get_sort_key(file_columns: List) -> str:
    for col in file_columns:
        if isinstance(col, list):
            return get_sort_key(col)
        if col.get("sort_key"):
            return col
    raise Exception(f"could not find a sort_key attr in {file_columns}")
