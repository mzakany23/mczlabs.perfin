import argparse

from perfin.cli import cli_args


def test_command(mocker):
    mocker.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=argparse.Namespace(accumulate=sum, integers=[1, 2, 3]),
    )
    args = cli_args()
    res = args.accumulate(args.integers)
    assert res == 6, "1 + 2 + 3 = 6"
