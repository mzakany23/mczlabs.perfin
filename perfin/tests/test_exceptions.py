from ..lib.file_matching.exceptions import MalformedParams, FileParseError

def test_exceptions_exist():
	assert MalformedParams
	assert FileParseError