import os
from pathlib import Path

from perfin.file_munging import get_file_names
from perfin.settings import config

TEST_FILE_DIR = "{}/files".format(os.path.dirname(os.path.abspath(__name__)))


def test_get_file_names(mocker):
    lookup = config.ACCOUNT_LOOKUP
    root_path = Path(TEST_FILE_DIR)
    file_names = get_file_names(lookup, root_path)
    filenames = [fn for fn in file_names]
    old_filename, new_filename = filenames[0]
    assert filenames
    assert isinstance(old_filename, Path)
    assert isinstance(new_filename, Path)


def test_get_file_rows():
    pass
