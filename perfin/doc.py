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

    def parse(self, doc:Dict):
        self.description = doc.get('description')
        self.original = doc.get('original')
        self.transaction_date = str(doc.get('transaction_date'))
        self.memo = doc.get('memo')
        self.transaction_type = doc.get('transaction_type')
        self.card_num = doc.get('card_num')
        self.debit = doc.get('debit')
        self.amount = doc.get('amount')
        self.credit = doc.get('credit')
        self.check_num = doc.get('check_num')
        self.transaction_posted_date = str(doc.get('transaction_posted_date'))
        self.category = doc.get('category')
        return self

Doc.register(FlatDoc)
