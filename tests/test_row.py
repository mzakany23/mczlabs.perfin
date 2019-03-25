import pytest
from ..lib.file_matching.analyzer import *
from ..lib.file_matching.config import *
from ..lib.file_matching.row import *

'''
    HOW_TO_RUN_TESTS
        make sure python tls is 1.2 compatable
        make sure pytest is installed
        (with warnings)
        pytest ./tests
        (without warnings)
        pytest -q ./tests -p no:warnings
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




# -------------------------------------------------------------------
# 1. fixtures
# -------------------------------------------------------------------


@pytest.fixture
def scenarios():
    return [
        {
            'filename' : 'mzakany-perfin/capitalone3507_Activity20190314.CSV',
            'data' : ['2018-10-08', '2018-10-09', '3457', 'HEROKU SEP-20833205', 'Internet', '14.00', '']
        }
    ]


# -------------------------------------------------------------------
# 2. unit tests (es access stubbed)
# -------------------------------------------------------------------


def test_unit(scenarios):
    for row_scenario in scenarios:

        analyzer = FileAnalyzer(
            header=row_scenario['data'],
            filename=row_scenario['filename']
        )

        policy = analyzer.policy 
        mapping = analyzer.mapping

        row = RowFactory(policy, row_scenario['data'])
        doc = row.get_doc()

        assert row.trim_key == 'description'
        assert mapping.success == True
        assert mapping.date.index == 1


# -------------------------------------------------------------------
# 3. integration tests (requires elasticsearch)
# -------------------------------------------------------------------


