from datetime import datetime

from pynamodb.attributes import UTCDateTimeAttribute, UnicodeAttribute
from pynamodb.models import Model


class PerfinBase(Model):
    last_updated = UTCDateTimeAttribute()
    created_at = UTCDateTimeAttribute(default=datetime.now)

    def save(self, *args, **kwargs):
        self.last_updated = datetime.now()
        super(PerfinBase, self).save(*args, **kwargs)


class PerfinAccount(PerfinBase):
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
