from datetime import datetime

from elasticsearch_dsl import Date, Document, Float, Keyword, Long, Text, connections
from loguru import logger

from .settings import DATE_FMT
from .util import generate_specific_key, make_key

es_config = {"hosts": ["localhost"], "timeout": 20}

connections.create_connection(**es_config)


def dfmt(date: datetime, date_fmt: str = DATE_FMT):
    return None if date is None else datetime.strftime(date, date_fmt)


def get_date(**kwargs):
    return Date(default_timezone="UTC", **kwargs)


class PerFinTransaction(Document):
    created_at = get_date()
    category = Keyword()
    aggregates = Keyword()
    account_name = Keyword()
    account_type = Keyword()
    amount = Float()
    description = Text(fielddata=True)
    original = Keyword()
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

    @staticmethod
    def create(**kwargs):
        doc = kwargs["doc"]
        doc_key = kwargs["doc_key"]
        doc_type = kwargs["doc_type"]

        aggregates = make_key(doc.get("description") or "")

        transaction = PerFinTransaction(
            account_name=doc_key,
            account_type=doc_type,
            aggregates=aggregates,
            description=doc.get("description"),
            trans_date=doc.get("transaction_date"),
            posted_date=doc.get("transaction_posted_date"),
            card_num=doc.get("card_num"),
            category=doc.get("category"),
            original=doc.get("original"),
            debit=doc.get("debit"),
            credit=doc.get("credit"),
            trans_type=doc.get("transaction_type"),
            amount=doc.get("amount"),
            memo=doc.get("memo"),
            check_num=doc.get("check_num"),
        )
        if not transaction.date:
            transaction.date = transaction.posted_date
        transaction.save()

    def save(self, **kwargs):
        self.created_at = datetime.utcnow()
        self.meta["id"] = generate_specific_key(
            self.description, dfmt(self.date), str(self.amount)
        )
        logger.info(f"inserting {self.__dict__}")
        return super().save(**kwargs)
