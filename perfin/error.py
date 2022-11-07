import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd
from loguru import logger

from .paths import ensure_dir


def handle_error(df: pd.DataFrame = None, file_meta: Dict = None, file:Any=None):
    dead_letter = "./files/errors/deadletter"
    ensure_dir(dead_letter)
    filename = file.path
    fp = "/".join(filename.split("/")[0:-1])

    if fp:
        path = f"{dead_letter}/{fp}"
        Path(path).mkdir(parents=True, exist_ok=True)

    dlf = f"{dead_letter}/{filename}"

    if df is None:
        with Path(dlf).open("w") as dlf_file:
            file.file.seek(0)
            dlf_file.write(file.file.read().decode("utf-8"))
            return
    else:
        df.to_csv(dlf)
    col = file_meta["file_columns"]
    schema_dir = ensure_dir("./files/errors/schema")


    expected = [item["column_name"] for item in col[0]]
    if isinstance(df, pd.core.indexes.base.Index):
        df = df.to_frame()
    path = Path(f"{schema_dir}/{filename}")
    got = [col for col in df.columns]
    remote_path = file_meta["file_path"]
    logger.warning(
        f"Error parsing! expected:{expected}, " f"got:{got}, file_path: {remote_path}"
    )

    with path.open("w") as file:
        json.dump(
            {
                "got": got,
                "expected": expected,
                "body": df.head().to_dict(),
                "meta": file_meta,
            },
            file,
            indent=4,
        )
