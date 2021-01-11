import os
from pathlib import Path

from perfin.file_munging import get_file_names
from perfin.settings import config

TEST_FILE_DIR = "{}/tests/files".format(os.path.dirname(os.path.abspath(__name__)))


def test_get_file_names(mocker):
    lookup = config.ACCOUNT_LOOKUP
    root_path = Path(TEST_FILE_DIR)
    file_names = get_file_names(lookup, root_path)
    assert [fn for fn in file_names]