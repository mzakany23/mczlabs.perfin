import datetime
from pathlib import Path

from perfin import DATE_FMT, get_files

"""
    how to run

    make test TEST_FILE=test_paths
"""


def test_get_file_names(csv_finder):
    """
        how to run

        make test TEST_FILE=test_paths TEST_FN=test_get_file_names
    """
    finder = csv_finder("chase_test_invert")

    for old_file, new_file_name in get_files(finder):
        parts = new_file_name.split("____")
        fd, td = parts[1].split("--")
        fd = datetime.datetime.strptime(fd, DATE_FMT)

        assert len(parts) == 3
        assert isinstance(fd, datetime.datetime)
        assert isinstance(old_file, Path)
        assert isinstance(new_file_name, str)
