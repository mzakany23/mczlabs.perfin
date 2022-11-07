from pathlib import Path

ROOT_PATH = Path("./tests/files").resolve()
SCHEMA = {
    "chase": {
        "file_name_search": ["chase"],
        "record_type": "credit_card",
        "file_columns": [
            [
                {
                    "column_name": "Transaction Date",
                    "key": "transaction_date",
                    "date_format": "%m/%d/%Y",
                    "schema_type": "date",
                },
                {
                    "column_name": "Post Date",
                    "sort_key": True,
                    "key": "transaction_posted_date",
                    "date_format": "%m/%d/%Y",
                    "schema_type": "date",
                },
                {
                    "column_name": "Description",
                    "key": "description",
                    "schema_type": "string",
                },
                {"column_name": "Category", "key": "category", "schema_type": "string"},
                {
                    "column_name": "Type",
                    "key": "transaction_type",
                    "schema_type": "string",
                },
                {"column_name": "Amount", "key": "amount", "schema_type": "float"},
                {"column_name": "Memo", "key": "memo", "schema_type": "string"},
            ],
            [
                {
                    "column_name": "Date",
                    "sort_key": True,
                    "key": "transaction_posted_date",
                    "date_format": ["%Y-%m-%d", "%m/%d/%Y"],
                    "schema_type": "date",
                },
                {
                    "column_name": "Description",
                    "key": "description",
                    "schema_type": "string",
                },
                {
                    "column_name": "Amount",
                    "key": "amount",
                    "invert_value": True,
                    "schema_type": "float",
                },
            ],
        ],
    },
    "fifth_third": {
        "file_name_search": ["fifth_third", "fifththird", "exports", "export", "53"],
        "record_type": "checking",
        "file_columns": [
            [
                {
                    "column_name": "Date",
                    "sort_key": True,
                    "date_format": "%m/%d/%Y",
                    "key": "transaction_posted_date",
                    "schema_type": "date",
                },
                {
                    "column_name": "Description",
                    "key": "description",
                    "schema_type": "string",
                },
                {
                    "column_name": "Check Number",
                    "key": "check_num",
                    "schema_type": "int",
                },
                {
                    "column_name": "Amount",
                    "key": "amount",
                    "invert_value": True,
                    "schema_type": "float",
                },
            ],
            [
                {
                    "column_name": "Date",
                    "sort_key": True,
                    "key": "transaction_posted_date",
                    "date_format": "%m/%d/%Y",
                    "schema_type": "date",
                },
                {
                    "column_name": "Description",
                    "key": "description",
                    "schema_type": "string",
                },
                {
                    "column_name": "Amount",
                    "key": "amount",
                    "invert_value": True,
                    "schema_type": "float",
                },
            ],
        ],
    },
    "capital_one": {
        "file_name_search": [
            "transaction_download",
            "capital_one",
            "capitalone",
            "capone",
        ],
        "record_type": "credit_card",
        "file_columns": [
            [
                {
                    "column_name": "Transaction Date",
                    "date_format": "%Y-%m-%d",
                    "key": "transaction_date",
                    "schema_type": "date",
                },
                {
                    "column_name": "Posted Date",
                    "sort_key": True,
                    "date_format": "%Y-%m-%d",
                    "key": "transaction_posted_date",
                    "schema_type": "date",
                },
                {
                    "column_name": ["Card Number", "Card No."],
                    "key": "card_num",
                    "schema_type": "int",
                },
                {
                    "column_name": "Description",
                    "key": "description",
                    "schema_type": "string",
                },
                {"column_name": "Category", "key": "category", "schema_type": "string"},
                {
                    "column_name": "Debit",
                    "invert_value": True,
                    "key": "debit",
                    "schema_type": "float",
                },
                {"column_name": "Credit", "key": "credit", "schema_type": "float"},
            ],
            [
                {
                    "column_name": "Date",
                    "sort_key": True,
                    "key": "transaction_posted_date",
                    "date_format": "%m/%d/%Y",
                    "schema_type": "date",
                },
                {
                    "column_name": "Description",
                    "key": "description",
                    "schema_type": "string",
                },
                {
                    "column_name": "Amount",
                    "key": "amount",
                    "invert_value": True,
                    "schema_type": "float",
                },
            ],
        ],
    },
}
