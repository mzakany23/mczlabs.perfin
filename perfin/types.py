import datetime
from typing import IO, Any, Callable, Dict, List, Tuple, Union

# yeah change this
FilePath = Any
DateFormat = Union[List[str], str]
File = IO
FileColumns = Tuple[List, str]
RowFieldValue = Union[float, str, int, datetime.datetime]
SchemaType = Union[float, str, int, datetime.datetime]
RowValue = List[Dict]
ParsedRows = List[Callable]
