import datetime
import mimetypes
from pathlib import Path

import pandas as pd

from .settings import config


def rename_files(lookup: dict, path: Path):
    for ofn, nfn in get_file_names(lookup, path):
        ofn.rename(nfn)


def get_file_names(lookup: dict, root_path: Path):
    for path in root_path.glob("*.csv"):
        file_name = path.name.lower()
        new_file_name = None
        account = None

        for key in list(lookup.keys()):
            account = lookup[key]
            if key in file_name:
                new_file_name = account["key"]
                break

        if not new_file_name and account:
            raise Exception(f"could not find a file name for {file_name}")

        df = pd.read_csv(f"{path}")

        try:
            sort_key = account["sort_key"]
            dates = df[sort_key].to_list()
        except KeyError:
            raise Exception(f"sort_key {sort_key} could not be found in config")

        if len(dates) == 1:
            dates = [datetime.datetime.strptime(dates[0], account["date_format"])]
        elif dates:
            try:
                dates.sort(
                    key=lambda date: datetime.datetime.strptime(
                        date, account["date_format"]
                    )
                )
                dates = [
                    datetime.datetime.strptime(date, account["date_format"])
                    for date in dates
                ]

            except ValueError:
                raise Exception("date format is incorrect")

        from_date = datetime.datetime.strftime(dates[0], config.DATE_FMT)
        to_date = datetime.datetime.strftime(dates[-1], config.DATE_FMT)

        fn = config.create_file_name(new_file_name, from_date, to_date)
        ofn = path.absolute()
        mt = mimetypes.guess_type(ofn.name)

        if not mt[0] == "text/csv":
            raise Exception("can only handle csv files")
        nfn = f"{path.parent}/{fn}.csv"
        yield ofn, Path(nfn)
