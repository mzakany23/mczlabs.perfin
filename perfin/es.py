from datetime import datetime

from elasticsearch_dsl import Date, Document, Float, Integer, Keyword, Text, connections
from perfin.settings import config

date_fmt = config.es_date_fmt

connections.create_connection(**config.es_config)


def get_date(format=date_fmt):
    return Date(format=date_fmt)


class Transaction(Document):
    created_at = get_date()
    category = Keyword()
    account = Keyword()
    amount = Float()
    description = Text(fielddata=True)
    check_num = Integer()
    date = get_date()
    posted_date = get_date()
    trans_date = get_date()
    trans_type = Keyword()
    credit = Float()
    debit = Float()

    class Index:
        name = "transactions"

    def save(self, **kwargs):
        self.created_at = datetime.utcnow()
        return super().save(**kwargs)
