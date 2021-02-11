from datetime import datetime

from elasticsearch_dsl import Date, Document, Float, Keyword, Long, Text, connections

from .settings import generate_specific_key

es_config = {"hosts": ["localhost"], "timeout": 20}

connections.create_connection(**es_config)


def get_date(**kwargs):
    return Date(default_timezone="UTC", **kwargs)


class Transaction(Document):
    created_at = get_date()
    category = Keyword()
    account_name = Keyword()
    account_type = Keyword()
    amount = Float()
    description = Text(fielddata=True)
    check_num = Long()
    date = get_date()
    posted_date = get_date()
    trans_date = get_date()
    trans_type = Keyword()
    credit = Float()
    debit = Float()
    key = Keyword()
    memo = Text(fielddata=True)

    class Index:
        name = "transactions"

    def save(self, **kwargs):
        self.created_at = datetime.utcnow()
        self.meta["id"] = generate_specific_key(
            self.description, self.dfmt(self.date), str(self.amount)
        )
        return super().save(**kwargs)
