import os
import mock
import pytest

from ..lib.file_matching.analyzer import FileAnalyzer
from ..util.es.es_conn import get_es_connection, insert_document
from ..handler import process_files

'''
    HOW_TO_RUN_TESTS
        pytest ./perfin/tests/test_handler.py -p no:warnings
        RUN_INTEGRATION_TESTS pytest ./perfin/tests/test_handler.py -p no:warnings
        RUN_LIVE_LOCAL_TESTS=1 pytest ./perfin/tests/test_handler.py -p no:warnings
'''

# -------------------------------------------------------------------
# LEGEND
# -------------------------------------------------------------------

'''
    0. test helpers
    1. fixtures
    2. unit tests (no db required)
    3. integration tests (elasticsearch required)
'''

# -------------------------------------------------------------------
# 0. test helpers
# -------------------------------------------------------------------

def local_process_files(event, context, es):
    file_paths = [record['s3']['object']['key'] for record in event["Records"]]
    for file_path in file_paths:
        analyzer = FileAnalyzer(file_path=file_path, trim_field='description', s3=False)
        for row in analyzer.get_rows():
            document = row["document"]
            document["group"] = row["_group"]
            index = 'transactions_write'
            insert_document(es, index, row["_id"], document)


def insert_fn(*args, **kwargs):
    return True


def read_csv_fn(*args, **kwargs):
    yield {
        'document' : {

        },
        '_group' : 'foo',
        '_id' : 'foo'
    }

class LocalFileAnalyzer(FileAnalyzer):
    def __init__(self, **kwargs):
        kwargs.setdefault('s3', False)
        super(LocalFileAnalyzer, self).__init__(**kwargs)


class FakeFileAnalyzer:
    def __init__(self, *args, **kwargs):
        pass

    def get_rows(self):
        return [
            {
              '_id': '3a34633eb9b64eaae92c5324f849b2caf9e5859dea6c24fce619110088efa24e',
              'document': {
                'account': 'CHASE',
                'post date': '2019-03-13',
                'description': 'CLEV HTS - PARKING',
                'category': 'Travel',
                'type': 'Sale',
                'amount': -0.75
              },
              '_group': 'CLEV HTS -'
            }
        ]

# -------------------------------------------------------------------
# 1. fixtures
# -------------------------------------------------------------------

@pytest.fixture
def desktop_file_paths():
    paths = []
    directory = os.path.expanduser('~/Desktop/perfin_files')
    for path in os.listdir(directory):
        if '____' in path:
            paths.append(f'{directory}/{path}')
    if not paths:
        raise Exception('there are no files in directory!')
    return paths


@pytest.fixture
def file_paths():
    directory = '{}/files'.format(os.path.dirname(os.path.abspath(__file__)))
    paths = []
    for path in os.listdir(directory):
        if '____' in path:
            paths.append(f'{directory}/{path}')
    return paths


@pytest.fixture
def event():
    return {
      'Records': [
        {
          's3': {
            's3SchemaVersion': '1.0',
            'configurationId': '07cdd4c6-53ea-41d1-9536-e64d6661708d',
            'bucket': {
              'name': 'mzakany-perfin',
              'ownerIdentity': {
                'principalId': 'A1KXLJ5C0RVBLI'
              },
              'arn': 'arn:aws:s3:::mzakany-perfin'
            },
            'object': {
              'key' : 'chase____2019.01.12.csv',
              'size': 2577,
              'eTag': '47eb72587b90a88cf07820543e938d11',
              'sequencer': '005BB006BB55D4F51F'
            }
          }
        }
      ]
    }


@pytest.fixture
def events(file_paths):
    records = {
      'Records': []
    }
    for local_file_path in file_paths:
        records['Records'].append({
          's3': {
            's3SchemaVersion': '1.0',
            'configurationId': '07cdd4c6-53ea-41d1-9536-e64d6661708d',
            'bucket': {
              'name': 'mzakany-perfin',
              'ownerIdentity': {
                'principalId': 'A1KXLJ5C0RVBLI'
              },
              'arn': 'arn:aws:s3:::mzakany-perfin'
            },
            'object': {
              'key' : local_file_path,
              'size': 2577,
              'eTag': '47eb72587b90a88cf07820543e938d11',
              'sequencer': '005BB006BB55D4F51F'
            }
          }
        })
    return records


@pytest.fixture
def local_events(desktop_file_paths):
    records = {
      'Records': []
    }
    for local_file_path in desktop_file_paths:
        records['Records'].append({
          's3': {
            's3SchemaVersion': '1.0',
            'configurationId': '07cdd4c6-53ea-41d1-9536-e64d6661708d',
            'bucket': {
              'name': 'mzakany-perfin',
              'ownerIdentity': {
                'principalId': 'A1KXLJ5C0RVBLI'
              },
              'arn': 'arn:aws:s3:::mzakany-perfin'
            },
            'object': {
              'key' : local_file_path,
              'size': 2577,
              'eTag': '47eb72587b90a88cf07820543e938d11',
              'sequencer': '005BB006BB55D4F51F'
            }
          }
        })
    return records


@pytest.fixture
def context():
    return {}

# -------------------------------------------------------------------
# 2. unit tests (es access stubbed)
# -------------------------------------------------------------------

@mock.patch('perfin.handler.insert_document', mock.MagicMock())
@mock.patch('perfin.handler.FileAnalyzer', FakeFileAnalyzer)
def test_process_files(event, context):
    files = process_files(event, context)
    assert files is None


@pytest.mark.skipif(not os.environ.get('RUN_INTEGRATION_TESTS'), reason="Does not have local elasticsearch running")
@mock.patch('perfin.handler.FileAnalyzer', LocalFileAnalyzer)
@mock.patch('perfin.tests.test_handler.process_files', local_process_files)
@mock.patch('perfin.handler.sentry_sdk', mock.MagicMock())
def test_integration(events, context):
    os.environ['ES_NODE'] = 'http://localhost:9200'
    es = get_es_connection()
    files = process_files(events, context, es)
    res = es.search('transactions_write')
    assert res['hits']['total'] == 292


@pytest.mark.skipif(not os.environ.get('RUN_LIVE_LOCAL_TESTS'), reason="Does not have local elasticsearch running")
@mock.patch('perfin.handler.FileAnalyzer', LocalFileAnalyzer)
@mock.patch('perfin.tests.test_handler.process_files', local_process_files)
@mock.patch('perfin.handler.sentry_sdk', mock.MagicMock())
def test_upload_generated_files(local_events, context):
    os.environ['ES_NODE'] = 'http://localhost:9200'
    es = get_es_connection()
    files = process_files(events, context, es)
    res = es.search('transactions_write')
