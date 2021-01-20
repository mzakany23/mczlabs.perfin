import logging

from .csv import Row, convert_field
from .paths import PathFinder

logger = logging.getLogger(__name__)


def get_transactions(finder: PathFinder):
    for account, path, df in finder.load_files():
        cols = [col for col in df.columns]
        account_name = account["account_name"]
        file_column_groups = account["file_columns"]

        if isinstance(file_column_groups[0], dict):
            file_column_groups = [file_column_groups]

        for file_columns in file_column_groups:
            try:
                assert len(df.columns) == len(file_columns)
            except AssertionError:
                spec = [f["key"] for f in file_columns]
                logger.warning(
                    f"\n{account_name} parsing error! Data frame shows {len(cols)} columns\ndf columns: {cols} \nspec columns: {spec}"
                )
                continue

            logger.info(f"successfully parsed {account_name}: {cols}")

            for _, row in df.iterrows():
                for i, stype in enumerate(file_columns):
                    stype["original_value"] = row[i]
                    stype["processed_value"] = convert_field(row[i], stype)
                    row[i] = stype

                yield Row(account_name, account["account_type"], row)
