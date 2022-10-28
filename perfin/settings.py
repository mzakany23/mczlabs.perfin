import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PerfinConfig:
    date_fmt:str = None
    file_dir:str = None
    bucket_path:str = None
    base_path:str = None

    def __post_init__(self):
        self.file_dir = self.file_dir or os.environ.get("FILE_DIR", Path("./files").resolve())
        self.bucket_path = self.bucket_path or os.environ.get("BUCKET_PATH", "mzakany-perfin")
        self.base_path = self.base_path or "~/Desktop"
        self.date_fmt = self.date_fmt or "%Y-%m-%d"

    def schema(self, path:str="./.config/accounts.json"):
        with Path(path).resolve().open("r") as file:
            return json.load(file)["ACCOUNT_LOOKUP"]

config = PerfinConfig()
