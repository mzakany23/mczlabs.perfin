import datetime
from typing import Any, Callable, Dict, List, Union

# yeah change this
FilePath = Any
DateFormat = Union[List[str], str]
RowFieldValue = Union[float, str, int, datetime.datetime]
SchemaType = Union[float, str, int, datetime.datetime]
RowValue = List[Dict]
ParsedRows = List[Callable]
