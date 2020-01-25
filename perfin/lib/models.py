from datetime import datetime

from pynamodb.attributes import UTCDateTimeAttribute, UnicodeAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex
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


class AccountNameIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "account_name_index"
        read_capacity_units = 1
        write_capacity_units = 2
        # All attributes from the table are projected here
        projection = AllProjection()
    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    account_name = UnicodeAttribute(hash_key=True)


class PerfinUploadLog(PerfinBase):
    class Meta:
        table_name = "perfin-upload-log"
        region = 'us-east-1'
        read_capacity_units = 1
        write_capacity_units = 1
    filename = UnicodeAttribute(hash_key=True)
    from_date = UnicodeAttribute()
    to_date = UnicodeAttribute()
    account_name = UnicodeAttribute()
    account_name_index = AccountNameIndex()
