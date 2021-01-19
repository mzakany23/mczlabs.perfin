import logging

from .csv import Row, convert_field
from .exceptions import PerfinColumnParseError
from .paths import PathFinder

logger = logging.getLogger(__name__)


def get_transactions(finder: PathFinder):
    for account, path, df in finder.load_files():
        for _, row in df.iterrows():
            file_columns = account["file_columns"]
            try:
                assert len(df.columns) == len(file_columns)
            except AssertionError:
                cols = [col for col in df.columns]
                spec = [f["key"] for f in file_columns]
                raise PerfinColumnParseError(
                    f"column error! Data frame shows {len(cols)} columns\ndf columns: {cols} \nspec columns: {spec}"
                )

            for i, stype in enumerate(file_columns):
                stype["original_value"] = row[i]
                stype["processed_value"] = convert_field(row[i], stype)
                row[i] = stype

            yield Row(account["account_name"], account["account_type"], row)
