import json
from datetime import datetime
from typing import Any, Callable, Dict, Tuple

import pandas as pd
from loguru import logger
from pydantic.dataclasses import dataclass
from pydantic.error_wrappers import ValidationError

from .doc import Doc, FlatDoc
from .error import handle_error
from .paths import LocalCSVFileFinder, S3CSVFileFinder, find_config, get_file_columns
from .settings import PerfinConfig, config
from .types import DateFormat, FilePath, RowFieldValue, SchemaType
from .util import convert_date, convert_float, convert_int, create_file_name

BUCKET_PATH = config.bucket_path
DATE_FMT = config.date_fmt


def get_csv_file_names(
    finder: LocalCSVFileFinder, to_path: str, schema: Dict
) -> Tuple[FilePath, str]:
    for file in finder.load_files():
        df = pd.read_csv(file, keep_default_na=False)
        file_meta = find_config(file.stem, schema)
        _, sort_key = get_file_columns(df, file_meta)
        column_name = sort_key["column_name"]
        dates = df[column_name].to_list()
        if not dates:
            logger.warning(f"found {file.stem} but is blank, so skipping...")
            continue
        date_format = sort_key["date_format"]
        config_key = file_meta["config_key"]
        dates = [convert_date(date, date_format) for date in dates]
        dates.sort()
        start_date = datetime.strftime(dates[0], DATE_FMT)
        end_date = datetime.strftime(dates[-1], DATE_FMT)
        new_file_name = f"{create_file_name(config_key, start_date, end_date)}.csv"

        yield file, to_path.joinpath(new_file_name)


@dataclass
class RowField:
    column_name: str = None
    key: str = None
    original_value: RowFieldValue = None
    processed_value: RowFieldValue = None
    date_format: DateFormat = None
    schema_type: SchemaType = None
    invert_value: bool = False
    sort_key: bool = None

    def get_type(self):
        field_lookup = {
            "date": convert_date,
            "float": convert_float,
            "int": convert_int,
        }
        return field_lookup.get(self.schema_type)

    def calculate(self):
        value = self.original_value
        fn = self.get_type()
        return value if not fn else fn(value, self.__dict__)


@dataclass
class CSVParsedFile:
    doc: Any
    doc_key: Any
    doc_type: Any


@dataclass
class CSVFileParser:
    file: FilePath
    parse_schema: Dict

    def get_rows(self) -> Dict:
        df, file_meta = None, None
        try:
            df = pd.read_csv(self.file.file, keep_default_na=False)
            file_name = self.file.path
            cols = [col for col in df.columns]
            file_meta = find_config(file_name, self.parse_schema)
            file_meta["file_path"] = file_name
            file_column, sort_key = get_file_columns(df, file_meta)

            logger.info(f"successfully parsed {file_name}: {cols}")

            if file_column and sort_key:
                for _, row in df.iterrows():
                    breakpoint()
                    doc = {}
                    for i, stype in enumerate(file_column):
                        try:
                            row_field = RowField(original_value=row[i], **stype)
                            doc[stype["key"]] = row_field.calculate()
                        except ValidationError as e:
                            raise Exception(f"ValidationError: {stype}") from e

                    doc["original"] = json.dumps(
                        {
                            "file_column": file_column,
                            "sort_key": sort_key,
                            "row": row.to_dict(),
                        }
                    )

                    yield CSVParsedFile(
                        doc=doc,
                        doc_key=file_meta["config_key"],
                        doc_type=file_meta["record_type"],
                    )
                else:
                    yield None
        except Exception as e:
            logger.warning(f"error parsing file {self.file.path}, {e}")
            handle_error(df, file_meta, self.file)


def csv_docs(
    base_path: str,
    schema: Dict,
    finder_cls: Callable = S3CSVFileFinder,
    doc_cls: Doc = None,
) -> Dict:
    finder = finder_cls(base_path=base_path)
    for file in finder.load_files():
        parser = CSVFileParser(file, schema)
        for row in parser.get_rows():
            if row is None:
                continue
            if doc_cls is not None:
                row.doc = doc_cls().parse(row)
            yield row


def csv_doc_batches(
    batches: int = 10,
    doc_cls: Callable = FlatDoc,
    finder_cls: Callable = S3CSVFileFinder,
    perfin_config: PerfinConfig = None,
):
    current = batches
    batch = []
    if perfin_config is None:
        perfin_config = config

    for i, row in enumerate(
        csv_docs(
            base_path=config.bucket_path,
            schema=config.schema(),
            finder_cls=finder_cls,
            doc_cls=FlatDoc,
        )
    ):
        batch.append(row.doc)

        if i == current - 1:
            yield batch
            current += batches
            batch = []

    if batch:
        yield batch
