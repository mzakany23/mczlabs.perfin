import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict


@dataclass
class Doc(ABC):
    @abstractmethod
    def parse(self, doc:Dict):
        pass


@dataclass
class FlatDoc(Doc):
    hash: str = None
    key: str = None
    date:str = None
    description: str = None
    original: str = None
    transaction_date: str = None
    memo: str = None
    transaction_type: str = None
    card_num: str = None
    debit: str = None
    amount: str = None
    credit: str = None
    check_num: str = None
    transaction_posted_date: str = None
    category: str = None

    def parse(self, row:Dict):
        doc = row['doc']
        hashed = hashlib.new('sha256')
        hashed.update(str(doc).encode('utf8'))
        self.hash = hashed.hexdigest()
        self.key = row['doc_key']
        self.description = doc.get('description')
        self.original = doc.get('original')
        self.memo = doc.get('memo')
        self.transaction_type = doc.get('transaction_type')
        self.card_num = doc.get('card_num')
        self.debit = doc.get('debit')
        self.amount = doc.get('amount')
        self.credit = doc.get('credit')
        self.check_num = doc.get('check_num')
        self.category = doc.get('category')
        self.transaction_date = doc.get('transaction_date')
        self.transaction_posted_date = doc.get('transaction_posted_date')
        self.date = str(doc.get(
            'date', self.transaction_date or self.transaction_posted_date)
        )
        return self

Doc.register(FlatDoc)
