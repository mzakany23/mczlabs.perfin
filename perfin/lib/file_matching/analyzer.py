import csv
import os

from s3fs.core import S3FileSystem

from .base import Base
from .exceptions import AccountParseError
from .mapping import Mapping
from .util.support import generate_specific_key


class FileAnalyzer(Base):
    def __init__(self, file_path, **kwargs):
        super(FileAnalyzer, self).__init__(**kwargs)
        self.file_path = file_path
        self.group_by = kwargs.get('group_by', 'description')
        self.s3 = kwargs.get('s3', True)
        self.trim_length = kwargs.get('trim_length', 10)
        filename = os.path.basename(self.file_path)
        if '____' not in filename:
            message = f'Account name {filename} is invalid.'
            raise AccountParseError(message)
        self.account_name = filename.split('____')[0].upper()
        self.reader = self.open_and_yield_csv_row(self.file_path)
        self.header = next(self.reader, None)
        self.mapping = Mapping(header=self.header)

    @property
    def __info__(self):
        self.matches.__info__

    @property
    def serialized_header(self):
        return '{}'.format(self.header)

    @property
    def schema(self):
        return self.mapping.schema

    def open_and_yield_csv_row(self, file_path):
        if self.s3:
            s3 = S3FileSystem(anon=False)
            _open = s3.open(file_path, mode="r")
        else:
            _open = open(file_path, mode="r")

        with _open as f:
            rows = csv.reader(f)
            for row in rows:
                yield row

    def get_rows(self):
        while True:
            row = next(self.reader, None)
            if not row:
                break
            yield self.build_doc(row, self.mapping)

    def build_doc(self, row, mapping):
        id_key = ",".join(row).replace(",", "").replace(" ", "")
        doc = {
            "_id" : generate_specific_key(id_key),
            "document" : {
                "account" : self.account_name
            }
        }

        for field in mapping.fields:
            value = field.process(row)
            doc['document'][field.key] = value

        doc["_group"] = doc['document'][self.group_by][:self.trim_length]
        return doc
