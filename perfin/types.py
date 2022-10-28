import datetime
import json
from datetime import date
from decimal import Decimal
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

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)
