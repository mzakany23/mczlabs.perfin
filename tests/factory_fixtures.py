import pandas
import pytest
from perfin.parsing import csv_docs as _csv_docs
from perfin.paths import LocalCSVFileFinder

from .util import ROOT_PATH, SCHEMA


@pytest.fixture
def csv_finder():
    def inner(file_name):
        base_path = ROOT_PATH.joinpath(f"{file_name}.csv").resolve()
        return LocalCSVFileFinder(base_path)

    return inner


@pytest.fixture
def csv_docs():
    def inner(file_name, fn=LocalCSVFileFinder):
        base_path = ROOT_PATH.joinpath(f"{file_name}.csv").resolve()
        return _csv_docs(base_path, SCHEMA, fn)

    return inner


@pytest.fixture
def df_finder(csv_finder):
    def inner(file_name="capone_test_basic"):
        finder = csv_finder(file_name)
        path = [path for path in finder.paths][0]
        return pandas.read_csv(f"{path}", keep_default_na=False)

    return inner
