from loguru import logger

from .accounts import get_file_columns
from .csv import Row, convert_field
from .paths import PathFinder


def get_transactions(finder: PathFinder):
    for account, path, df in finder.load_files():
        cols = [col for col in df.columns]
        account_name = account["account_name"]
        file_column, sort_key = get_file_columns(df, account)
        logger.info(f"successfully parsed {account_name}: {cols}")

        for _, row in df.iterrows():
            fields = []
            for i, stype in enumerate(file_column):
                stype["original_value"] = row[i]
                stype["processed_value"] = convert_field(row[i], stype)
                fields.append(stype)

            yield Row(account_name, account["account_type"], fields)
