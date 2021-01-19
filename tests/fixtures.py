import pytest
from perfin.paths import PathFinder
from perfin.settings import config


@pytest.fixture
def finder():
    path = config.root_path.joinpath("tests/files")
    return PathFinder(csv_path=path)
