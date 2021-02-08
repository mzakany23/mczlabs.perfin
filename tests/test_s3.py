from perfin.s3 import load_s3_files

"""
    how to run

    make test TEST_FILE=test_s3
"""

directory = "mzakany-perfin"


def test_get_s3_conn(mock_s3):
    """
        how to run

        make test TEST_FILE=test_s3 TEST_FN=test_get_s3_conn
    """
    fn = "mzakany-perfin/capital_one____2020-08-12--2020-12-04____f43fdfc292.csv"

    for account, file_path, df in load_s3_files(directory):
        assert account["account_name"] == "capital_one"
        assert file_path == fn

    mock_s3.ls.assert_called_once()
