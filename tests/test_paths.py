"""
    how to run

    make test TEST_FILE=test_paths
"""
import json
from pathlib import Path

import pandas
import pytest
from perfin.paths import (
    LocalCSVFileFinder,
    S3CSVFileFinder,
    find_config,
    get_file_columns,
    get_sort_key,
)

path = Path("./.config/accounts.json").resolve()

with path.open("r") as file:
    SCHEMA = json.load(file)["ACCOUNT_LOOKUP"]


def test_get_s3_conn(mocker):
    """
        how to run

        make test TEST_FILE=test_paths TEST_FN=test_get_s3_conn
    """
    mocker.patch("perfin.paths.S3FileSystem")
    finder = S3CSVFileFinder(base_path="foo")
    assert finder.get_s3_conn()


def test_load_file(mocker):
    """
        how to run

        make test TEST_FILE=test_paths TEST_FN=test_load_file
    """
    mocker.patch("perfin.paths.S3CSVFileFinder.get_s3_conn")
    finder = S3CSVFileFinder(base_path="foo")
    for file_path in finder.load_files():
        assert isinstance(file_path, str)


def test_get_file_columns(mocker, csv_finder):
    """
        how to run

        make test TEST_FILE=test_paths TEST_FN=test_get_file_columns
    """
    finder = csv_finder("capone_test_basic")
    for file in finder.load_files():
        df = pandas.read_csv(file, keep_default_na=False)
        file, sort_key = get_file_columns(df, SCHEMA["capital_one"])
        assert isinstance(file, list)
        assert isinstance(sort_key, dict)


def test_get_file_columns_inner(mocker, csv_finder):
    """
        how to run

        make test TEST_FILE=test_paths TEST_FN=test_get_file_columns_inne
    """
    with pytest.raises(Exception):
        finder = csv_finder("capone_test_basic")
        for file in finder.load_files():
            df = pandas.read_csv(file, keep_default_na=False)
            meta = {
                "file_columns": [
                    [
                        {"column_name": ["date"]},
                        {
                            "column_name": "Description",
                            "key": "description",
                            "schema_type": "string",
                        },
                        {
                            "column_name": "Category",
                            "key": "category",
                            "schema_type": "string",
                        },
                    ]
                ]
            }
            file, sort_key = get_file_columns(df, meta)
            assert isinstance(file, list)
            assert isinstance(sort_key, dict)


def test_get_file_columns_fail(mocker, csv_finder):
    """
        how to run

        make test TEST_FILE=test_paths TEST_FN=test_get_file_columns_fail
    """
    finder = csv_finder("capone_test_basic")
    side_effect = mocker.MagicMock(side_effect=AssertionError("foogazi"))

    mocker.patch(
        "perfin.paths.len", side_effect,
    )

    with pytest.raises(Exception):
        for file in finder.load_files():
            df = pandas.read_csv(file, keep_default_na=False)
            file, sort_key = get_file_columns(df, SCHEMA["capital_one"])
            assert isinstance(file, list)
            assert isinstance(sort_key, dict)


def test_find_config(mocker, csv_finder):
    """
        how to run

        make test TEST_FILE=test_paths TEST_FN=test_find_config
    """
    with pytest.raises(Exception):
        find_config("foo", {})


def test_get_sort_key(mocker, csv_finder):
    """
        how to run

        make test TEST_FILE=test_paths TEST_FN=test_get_sort_key
    """
    with pytest.raises(Exception):
        get_sort_key([[]])


def test_get_paths():
    """
        how to run

        make test TEST_FILE=test_paths TEST_FN=test_get_paths
    """
    finder = LocalCSVFileFinder("./files")
    for file in finder.get_paths():
        assert file


def test_move_paths(mocker):
    """
        how to run

        make test TEST_FILE=test_paths TEST_FN=test_move_paths
    """
    foo = mocker.MagicMock(name="foo")
    bar = mocker.MagicMock(name="foo")
    local_finder = LocalCSVFileFinder("./tests/files")
    local_finder.move(foo, bar)
    assert foo.rename.called
