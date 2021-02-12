from pathlib import Path
from typing import Dict

import pandas
from loguru import logger
from pydantic.dataclasses import dataclass
from pydantic.error_wrappers import ValidationError

from .paths import LocalCSVFileFinder, find_config, get_file_columns
from .types import DateFormat, RowFieldValue, SchemaType
from .util import convert_date, convert_float, convert_int


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
class CSVFileParser:
    file: Path
    parse_schema: Dict

    def get_rows(self) -> Dict:
        df = pandas.read_csv(self.file, keep_default_na=False)
        file_name = self.file.stem
        cols = [col for col in df.columns]
        file_meta = find_config(file_name, self.parse_schema)
        file_column, sort_key = get_file_columns(df, file_meta)

        logger.info(f"successfully parsed {file_name}: {cols}")

        for _, row in df.iterrows():
            doc = {}

            for i, stype in enumerate(file_column):
                key = stype["key"]

                try:
                    row_field = RowField(original_value=row[i], **stype)
                    doc[key] = row_field.calculate()
                except ValidationError as e:
                    raise Exception(f"ValidationError: {stype}") from e

            yield {
                "doc": doc,
                "doc_key": file_meta["config_key"],
                "doc_type": file_meta["record_type"],
            }


def csv_docs(base_path, schema, finder_cls=LocalCSVFileFinder):
    finder = finder_cls(base_path=base_path)

    for file in finder.load_files():
        parser = CSVFileParser(file, schema)
        for row in parser.get_rows():
            yield row
