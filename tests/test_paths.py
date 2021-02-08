import datetime
import os
from pathlib import Path

from perfin.paths import get_file_names
from perfin.settings import config

TEST_FILE_DIR = "{}/files".format(os.path.dirname(os.path.abspath(__name__)))

"""
    how to run

    make test TEST_FILE=test_paths
"""


def test_path_finder(mocker, finder):
    """
        how to run

        make test TEST_FILE=test_paths TEST_FN=test_path_finder
    """
    file = next(finder.paths)
    assert file.suffix == ".csv"
    assert finder.csv_patterns == ["*.csv", "*.CSV"]
    assert hasattr(finder, "load_files")


def test_get_file_names(csv_finder):
    """
        how to run

        make test TEST_FILE=test_paths TEST_FN=test_get_file_names
    """
    finder = csv_finder("chase_test_invert")
    for old_file, new_file_name in get_file_names(finder):
        parts = new_file_name.split("____")
        fd, td = parts[1].split("--")
        fd = datetime.datetime.strptime(fd, config.date_fmt)

        assert len(parts) == 3
        assert isinstance(fd, datetime.datetime)
        assert isinstance(old_file, Path)
        assert isinstance(new_file_name, str)
