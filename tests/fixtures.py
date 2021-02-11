from contextlib import contextmanager

import pytest
from perfin.paths import PathFinder

from .util import ROOT_PATH, SCHEMA


@pytest.fixture
def mock_s3(mocker):
    mocked_parent = mocker.MagicMock(name="Fake s3 conn")
    mocked_child = mocker.MagicMock(name="Fake s3 conn return")
    mocked_child.return_value.open = mock_open
    mocked_child.return_value.ls.return_value = [
        "mzakany-perfin/capital_one____2020-08-12--2020-12-04____f43fdfc292.csv"
    ]
    mocked_parent.return_value = mocked_child
    mocker.patch("perfin.s3.get_s3_conn", mocked_parent)
    return mocked_child


@pytest.fixture
def finder():
    return PathFinder(csv_path=ROOT_PATH, schema=SCHEMA)


@pytest.fixture
def schema():
    return SCHEMA


@contextmanager
def mock_open(finder):
    yield next(finder.paths)
