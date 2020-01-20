from datetime import datetime

from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute
from pynamodb.models import Model


class PerfinAccount(Model):
    class Meta:
        table_name = "perfin-account"
        region = 'us-east-1'
        read_capacity_units = 1
        write_capacity_units = 1
    item = UnicodeAttribute(hash_key=True)
    username = UnicodeAttribute()
    token = UnicodeAttribute()
    account_name = UnicodeAttribute()
    first_name = UnicodeAttribute()
    last_name = UnicodeAttribute()
    last_updated = UTCDateTimeAttribute()
    created_at = UTCDateTimeAttribute(default=datetime.now)

