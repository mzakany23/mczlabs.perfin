import datetime
from enum import Enum
from typing import Dict, List, Union

DateFormat = Union[List[str], str]
RowFieldValue = Union[float, str, int, datetime.datetime]
SchemaType = Union[float, str, int, datetime.datetime]
RowValue = List[Dict]


class GlobalVars(Enum):
    ALIAS_FIELD_NAME = "__alias_keys__"


ALIAS_FIELD_NAME = GlobalVars.ALIAS_FIELD_NAME.value
