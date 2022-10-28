from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from loguru import logger
from pandas import DataFrame
from s3fs import S3FileSystem

from .types import File, FileColumns

S3 = None

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

    def load_files(self) -> Path:
        for path in self.get_paths():
            yield path

    def move(self, file, new_path):
        new_path = new_path.joinpath(file.name)
        file.rename(new_path)


@dataclass
class S3CSVFileFinder:
    base_path: str
    patterns: List = field(default_factory=lambda: ["*.csv", "*.CSV"])

    def get_s3_conn(self):
        global S3
        return S3 if S3 else S3FileSystem(anon=False)

    def load_files(self) -> File:
        get_s3_conn = self.get_s3_conn

        for file_path in get_s3_conn().ls(self.base_path):
            path = Path(file_path)
            with get_s3_conn().open(file_path, mode="r") as file:
                file.stem = path.stem
                yield file

    def move(self, file: Path):
        filename = f"{self.base_path}/{file.name}"
        self.get_s3_conn().put(str(file), filename)


def get_file_columns(df: DataFrame, config_meta: Dict) -> FileColumns:
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
