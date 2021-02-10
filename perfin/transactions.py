from loguru import logger
from pydantic.error_wrappers import ValidationError

from .accounts import get_file_columns
from .csv import Row, RowField, convert_field
from .paths import PathFinder
from .types import ALIAS_FIELD_NAME


def get_transactions(finder: PathFinder):
    for account, path, df in finder.load_files():
        cols = [col for col in df.columns]
        account_name = account["account_name"]
        file_column, sort_key = get_file_columns(df, account)

        logger.info(f"successfully parsed {account_name}: {cols}")

        for _, row in df.iterrows():
            processed_fields = []
            schema_keys = []
            field_lookup = {ALIAS_FIELD_NAME: {}}

            for i, stype in enumerate(file_column):
                key = stype["key"]
                stype["original_value"] = row[i]
                stype["processed_value"] = convert_field(row[i], stype)
                alias_key = stype.get("alias")
                schema_keys.append(key)

                if alias_key:
                    field_lookup[ALIAS_FIELD_NAME][alias_key] = i
                    schema_keys.append(alias_key)
                try:
                    processed_fields.append(RowField(**stype))
                except ValidationError as e:
                    raise Exception(f"ValidationError: {stype}") from e

                field_lookup[key] = i

            yield Row(
                account_name,
                account["account_type"],
                field_lookup,
                schema_keys,
                processed_fields,
            )
