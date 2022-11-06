import json
from datetime import datetime
from pathlib import Path
from typing import Dict

import pandas as pd
from loguru import logger

from .paths import ensure_dir


def handle_error(df: pd.DataFrame, file_meta: Dict):
    col = file_meta["file_columns"]
    dead_letter = "./files/errors/deadletter"
    schema_dir = ensure_dir("./files/errors/schema")
    deadletter_dir = ensure_dir(dead_letter)

    expected = [item["column_name"] for item in col[0]]
    if isinstance(df, pd.core.indexes.base.Index):
        df = df.to_frame()
    filename = datetime.utcnow().strftime("%Y%m%dT%H%M%S%f")
    path = Path(f"{schema_dir}/{filename}.json")
    got = [col for col in df.columns]
    remote_path = file_meta["file_path"]
    logger.warning(
        f"Error parsing! expected:{expected}, "
        f"got:{got}, file_path: {remote_path}"
    )
    df.to_csv(f"{deadletter_dir}/{filename}.csv")

    with path.open("w") as file:
        json.dump(
            {
                "got": got,
                "expected": expected,
                "body": df.head().to_dict(),
                "meta": file_meta,
            },
            file,
            indent=4
        )
