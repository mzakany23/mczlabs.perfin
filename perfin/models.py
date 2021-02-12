import csv
from datetime import datetime

from elasticsearch_dsl import Date, Document, Float, Keyword, Long, Text, connections
from s3fs import S3FileSystem

from .settings import DATE_FMT
from .util import generate_specific_key, make_key

S3 = None


es_config = {"hosts": ["localhost"], "timeout": 20}

connections.create_connection(**es_config)


def dfmt(d):
    return None if d is None else datetime.strftime(d, DATE_FMT)


def get_date(**kwargs):
    return Date(default_timezone="UTC", **kwargs)


class PerFinTransaction(Document):
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

    @staticmethod
    def create(file_key, **kwargs):
        doc = kwargs["doc"]
        doc_key = kwargs["doc_key"]
        doc_type = kwargs["doc_type"]

        description = make_key(doc.get("description") or "")

        transaction = PerFinTransaction(
            account_name=doc_key,
            account_type=doc_type,
            trans_date=doc.get("transaction_date"),
            posted_date=doc.get("transaction_posted_date"),
            card_num=doc.get("card_num"),
            description=description,
            category=doc.get("category"),
            debit=doc.get("debit"),
            credit=doc.get("credit"),
            trans_type=doc.get("transaction_type"),
            amount=doc.get("amount"),
            memo=doc.get("memo"),
            check_num=doc.get("check_num"),
        )

        transaction.save()

    def save(self, **kwargs):
        self.created_at = datetime.utcnow()
        self.meta["id"] = generate_specific_key(
            self.description, dfmt(self.date), str(self.amount)
        )
        return super().save(**kwargs)


def get_s3_conn():
    global S3
    return S3 if S3 else S3FileSystem(anon=False)


def get_s3_full_file_paths(directory: str, filter_key: str = None):
    for s3_file_path in get_s3_conn().ls(directory):
        if filter_key:
            if filter_key in s3_file_path:
                yield s3_file_path
        else:
            yield s3_file_path


def get_s3_rows(file_path: str):
    with get_s3_conn().open(file_path, mode="r") as file:
        yield from csv.reader(file)
