import datetime
from typing import Callable, Dict, List, Union

DateFormat = Union[List[str], str]
RowFieldValue = Union[float, str, int, datetime.datetime]
SchemaType = Union[float, str, int, datetime.datetime]
RowValue = List[Dict]
ParsedRows = List[Callable]
