from loguru import logger

from .settings import config


def get_file_columns(df, account):
    file_column_groups = account["file_columns"]

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


def get_sort_key(file_columns):
    for col in file_columns:
        if isinstance(col, list):
            return get_sort_key(col)
        if col.get("sort_key"):
            return col
    raise Exception(f"could not find a sort_key attr in {file_columns}")


def find_account(search_name):
    for account_name, account_config in config.ACCOUNT_LOOKUP.items():
        for account_alias in account_config["file_name_search"]:
            alias_match = account_alias.lower() in search_name
            if alias_match:
                account_config["account_name"] = account_name
                return account_config
