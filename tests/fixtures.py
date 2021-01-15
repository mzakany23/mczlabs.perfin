import pytest
from perfin.settings import config


@pytest.fixture
def file_dir():
    return config.root.joinpath("tests/files")
