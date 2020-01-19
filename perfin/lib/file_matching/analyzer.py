import csv
import os

from s3fs.core import S3FileSystem

from .base import Base
from .exceptions import AccountParseError
from .mapping import Mapping
from .util.support import generate_specific_key


class FileAnalyzer(Base):
    def __init__(self, *args, **kwargs):
        super(FileAnalyzer, self).__init__(**kwargs)

        if len(args) == 3:
            self.file_path, self.header, self.rows = args[0], args[1], args[2]
        else:
            if args:
                self.file_path = args[0]
            else:
                self.file_path = kwargs.get('file_path')
            self.s3 = kwargs.get('s3', True)
            self.reader = self.open_and_yield_csv_row(self.file_path)
            self.header = next(self.reader, None)
        filename = os.path.basename(self.file_path)
        if '____' not in filename:
            message = 'Account name {} is invalid.'.format(filename)
            raise AccountParseError(message)
        self.trim_length = kwargs.get('trim_length', 10)
        self.account_name = filename.split('____')[0].upper()
        self.group_by = kwargs.get('group_by', 'description')
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

    def open_and_yield_csv_row(self, file_path=None):
        if not file_path:
            file_path = self.file_path
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
        if hasattr(self, 'rows'):
            for row in self.rows:
                yield self.build_doc(row, self.mapping)
        elif hasattr(self, 'reader'):
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
