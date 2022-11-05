import json
from datetime import datetime
from pathlib import Path
from typing import List

from elasticsearch_dsl import Date, Document, Float, Keyword, Long, Text, connections
from loguru import logger
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, relationship

from .doc import Doc
from .settings import config
from .util import generate_specific_key, make_key

ES = None
# using postgresql@14
PG_URL = "postgresql://localhost:5432/perfin"
PG = declarative_base()


def dfmt(d):
    return None if d is None else datetime.strftime(d, config.date_fmt)


def get_date(**kwargs):
    return Date(default_timezone="UTC", **kwargs)


class ESPerFinTransaction(Document):
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

        transaction = ESPerFinTransaction(
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


class ESPerfinPG(PG):
    __tablename__ = "perfin"
    id = Column(Integer, primary_key=True)
    hash = Column(String, nullable=True)
    date = Column(DateTime, nullable=True)
    transaction_date = Column(DateTime, nullable=True)
    transaction_posted_date = Column(DateTime, nullable=True)
    description = Column(String, nullable=True)
    original = Column(String, nullable=True)
    memo = Column(String, nullable=True)
    transaction_type = Column(String, nullable=True)
    card_num = Column(String, nullable=True)
    debit = Column(String, nullable=True)
    amount = Column(String, nullable=True)
    credit = Column(String, nullable=True)
    check_num = Column(String, nullable=True)
    category = Column(String, nullable=True)
    doc_key = relationship("DocKey")
    doc_key_id = Column(Integer, ForeignKey("doc_key.id"))


class DocKey(PG):
    __tablename__ = "doc_key"
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True)


def get_es():
    global ES
    ES = connections.create_connection(**{"hosts": ["localhost"], "timeout": 20})
    return ESPerFinTransaction


def get_pg():
    return Session(create_engine(PG_URL, future=True))


def create_pg_tables():
    engine = create_engine(PG_URL, future=True)
    PG.metadata.create_all(engine)


def seed_pg_tables(path):
    with get_pg() as session:
        with Path(path).open("r") as file:
            for key in json.load(file)["ACCOUNT_LOOKUP"].keys():
                session.add(DocKey(key=key))
        session.commit()


def create_pg_docs(docs: List[Doc]):
    with get_pg() as session:
        batch = []
        key_cache = {
            doc_key.key: {"id": doc_key.id, "obj": doc_key}
            for doc_key in session.query(DocKey).all()
        }
        for doc in docs:
            cache = key_cache[doc.key]
            key = cache["obj"]
            key_id = cache["id"]

            if session.query(ESPerfinPG).filter_by(hash=doc.hash).first():
                continue

            item = ESPerfinPG(
                hash=doc.hash,
                description=doc.description,
                original=doc.original,
                transaction_date=doc.transaction_date,
                memo=doc.memo,
                transaction_type=doc.transaction_type,
                card_num=doc.card_num,
                debit=doc.debit,
                amount=doc.amount,
                credit=doc.credit,
                check_num=doc.check_num,
                transaction_posted_date=doc.transaction_posted_date,
                category=doc.category,
                doc_key=key,
                doc_key_id=key_id,
            )
            batch.append(item)
        session.add_all(batch)
        session.commit()
