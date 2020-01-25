from datetime import datetime

from pynamodb.attributes import UTCDateTimeAttribute
from pynamodb.models import Model


class PerfinBase(Model):
    last_updated = UTCDateTimeAttribute()
    created_at = UTCDateTimeAttribute(default=datetime.now)

    @staticmethod
    def create_table(self):
        Session.create_table(wait=True)
