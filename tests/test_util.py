from datetime import datetime

from perfin.util import (
    convert_date,
    convert_float,
    convert_int,
    create_file_name,
    generate_better_key,
    generate_specific_key,
    make_key,
)

"""
    how to run

    make test TEST_FILE=test_parsing
"""


def test_convert_date():
    """
    how to run

    make test TEST_FILE=test_util TEST_FN=test_convert_date
    """

    date = convert_date("2020-01-01", "%Y-%m-%d")
    assert type(date) == datetime


def test_convert_float():
    """
    how to run

    make test TEST_FILE=test_util TEST_FN=test_convert_float
    """
    assert convert_float("0.0") == 0.0


def test_convert_int():
    """
    how to run

    make test TEST_FILE=test_util TEST_FN=test_convert_int
    """
    assert convert_int("1") == 1


def test_create_file_name():
    """
    how to run

    make test TEST_FILE=test_util TEST_FN=test_create_file_name
    """
    fd, td = "2020-01-01", "2020-02-02"
    name = "foo"
    fn = create_file_name(name, fd, td)

    assert "____".join(fn.split("____")[0:2]) == "foo____2020-01-01--2020-02-02"


def test_generate_better_key():
    """
    how to run

    make test TEST_FILE=test_util TEST_FN=test_generate_better_key
    """
    assert len(generate_better_key()) == 64


def test_generate_specific_key():
    """
    how to run

    make test TEST_FILE=test_util TEST_FN=test_generate_specific_key
    """
    assert (
        generate_specific_key("foo", "bar", "baz")
        == "97df3588b5a3f24babc3851b372f0ba71a9dcdded43b14b9d06961bfc1707d9d"
    )


def test_make_key():
    """
    how to run

    make test TEST_FILE=test_util TEST_FN=test_make_key
    """
    assert make_key("foo bar") == "FOOBAR"
