import os
import pytest
from perfin.lib.file_matching.analyzer import FileAnalyzer
from perfin.util.csv_functions import open_and_yield_csv_row, get_files


'''
    HOW_TO_RUN_TESTS
        pytest ./perfin/tests/test_matching.py -p no:warnings
        pytest ./perfin/tests/test_matching.py -k 'test_poor_results test_fifth_third' -p no:warnings
'''

def test_get_docs():
    directory = '{}/files'.format(os.path.dirname(os.path.abspath(__file__)))

    for file_url, filename, ext in get_files(directory, '.csv'):
        assert file_url


def test_very_poor_results():
    domain = 'CHASE'
    header = ['foo', 'bar', 'baz']
    file_url = 'mzakany-perfin/Chase3507_Activity20190314.CSV'
    analyzer = FileAnalyzer(header=header, filename=file_url)
    assert analyzer.score.confidence == 'marginal' 
    assert analyzer.top_match.domain == domain


def test_poor_results():
    domain = 'CHASE'
    header = ['Type', 'Trans Date', 'Post Date']
    file_url = 'mzakany-perfin/Chase3507_Activity20190314.CSV'
    analyzer = FileAnalyzer(header=header, filename=file_url)
    assert analyzer.score.confidence == 'likely'
    assert analyzer.top_match.domain == domain


def test_chase():
    domain = 'CHASE'
    filename = 'mzakany-perfin/Chase3507_Activity20190314.CSV'
    header = ['Transaction Date', 'Post Date', 'Description', 'Category', 'Type', 'Amount']
    analyzer = FileAnalyzer(header=header, filename=filename)
    assert analyzer.top_match.domain == domain


def test_capone():
    domain = 'CAPITAL_ONE'
    filename = 'mzakany-perfin/CapitalOne3507_Activity20190314.CSV'
    header = [' Transaction Date', ' Posted Date', ' Card No.', ' Description', ' Category', ' Debit', ' Credit']
    analyzer = FileAnalyzer(header=header, filename=filename)
    assert analyzer.top_match.domain == domain


def test_fifth_third_ambiguous():
    domain = 'CHASE'
    filename = 'mzakany-perfin/FifthThird3507_Activity20190314.CSV'
    header = ['Type','TransDate','PostDate','Description','Amount']
    analyzer = FileAnalyzer(header=header, filename=filename)
    assert analyzer.top_match.domain == domain


def test_chase_signature():
    domain = 'CHASE'
    filename = 'mzakany-perfin/chase_financial.CSV'
    header = ['Type','Trans Date','Post Date','Description','Amount']
    analyzer = FileAnalyzer(header=header, filename=filename)
    assert analyzer.top_match.domain == domain


def test_ambiguous():    
    domain = 'CHASE'
    header = ['Type','Trans Date','Post Date','Description','Amount']
    filename = 'mzakany-perfin/fifth_third3507_Activity20190314.CSV'
    analyzer = FileAnalyzer(header=header, filename=filename)
    assert analyzer.score.confidence == 'likely'
    