import pytest
from perfin.settings import config


@pytest.fixture
def file_dir():
    return config.root_path.joinpath("tests/files")
