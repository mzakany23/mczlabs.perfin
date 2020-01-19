import functools

import re

from dateutil.parser import parse

from .base import Base
from .util.support import word_in_string


class MappingType(Base):
    def __init__(self, *args, **kwargs):
        super(MappingType, self).__init__(*args, **kwargs)
        self.validate(['key', 'index', 'columns'])
        self._key = kwargs.get('key')
        self._index = kwargs.get('index')
        self.columns = kwargs.get('columns')
        self.set_types()

    @property
    def __info__(self):
        self.header_print('Mapping info')
        self.pretty_print(self.data)

    @property
    def success(self):
        return self.has('key') and self.has('index')

    @property
    def data(self):
        return {
            'type' : self.columns
        }

    def parse_float(self, row):
        item = self.get_field(row)
        if not item:
            return 0.0
        try:
            item = float(item)
        except:
            item = False

            for field in row:
                try:
                    item = float(field)
                except:
                    pass
                if item:
                    break
        return 0.0 if not item else item

    def get_keys(self, item):
        return list(map(lambda x: x.lower(), item.strip().split(' ')))

    def has_classification(self, item):
        checks = self.get_keys(item)
        for item in self.classification:
            if item in checks:
                return True

    def set_types(self):
        matches = {}
        for i, item in enumerate(self.columns):
            if self.has_classification(item):
                matches[i] = item

        if self._index in matches:
            if hasattr(self, 'name'):
                self.key = self.name
            else:
                self.key = self.get_type(self._key)
            self.index = self._index
            self.value = self.columns[self.index]
        elif len(self.columns) >= self._index:
            self.key = self._key
            self.index = self._index
            self.value = self.columns[self._index]

    def process(self, row):
        return self.get_field(row)

    def get_field(self, row):
        return row[self.index]

    def post_process(self):
        if self.has('process'):
            if self.has('processor_functions'):
                self.processor_functions.append('process')
            else:
                self.processor_functions = ['process']

        if self.has('process') or self.has('processor_functions'):
            return (
                functools.reduce(
                    (lambda accum, fn: getattr(self, fn)(accum)),
                    self.processor_functions, self.value
                )
            )

    def get_type(self, key):
        for item in self.classification:
            found = word_in_string(key, item)
            if found:
                return found


class DateMappingType(MappingType):
    name = 'date'
    classification = ['date', 'post date']

    def process(self, row):
        try:
            return parse(self.get_field(row)).strftime("%Y-%m-%d")
        except:
            item = False
            for field in row:
                try:
                    found = parse(field).strftime("%Y-%m-%d")
                except:
                    found = False
                if found:
                    item = found
                    break
            if not item:
                return None
            return item


class TypeMappingType(MappingType):
    name = 'type'
    classification = ['type']


class DescriptionMappingType(MappingType):
    name = 'description'
    classification = ['description', 'transaction', 'name']


class AmountMappingType(MappingType):
    name = 'amount'
    classification = ['amount', 'debit']

    def process(self, row):
        return self.parse_float(row)


class CardMappingType(MappingType):
    name = 'card'
    classification = ['card']


class CategoryMappingType(MappingType):
    name = 'category'
    classification = ['category']


class CreditMappingType(MappingType):
    name = 'credit'
    classification = ['credit']

    def process(self, row):
        return self.parse_float(row)


class GenericMappingType(MappingType):
    name = 'general'
    classification = []


class Mapping(Base):
    DEFAULT_TYPES = [
        DateMappingType,
        TypeMappingType,
        DescriptionMappingType,
        AmountMappingType,
        CardMappingType,
        CategoryMappingType,
        CreditMappingType
    ]

    def __init__(self, *args, **kwargs):
        super(Mapping, self).__init__(*args, **kwargs)
        self.validate(['header'])
        self.header = kwargs.get('header')
        self.fields = []
        self.lookup = {}
        self.init_lookup()
        self.set_types()

    @property
    def __info__(self):
        self.header_print('Schema')
        return self.pretty_print(self.schema)

    def init_lookup(self):
        for _type in self.DEFAULT_TYPES:
            self.lookup[_type.name] = _type

    def set_types(self):
        _columns = {}
        for i, header in enumerate(self.header):
            for mapping_type in self.DEFAULT_TYPES:
                header = header.lower()
                header_match = False
                for key in mapping_type.classification:
                    key = re.sub(r'\s+', '', key)
                    if key in header:
                        header_match = True
                        break
                if header_match:
                    mapping = mapping_type(
                        key=header,
                        index=i,
                        columns=self.header
                    )
                    if mapping.success:
                        self.fields.append(mapping)
                        self.set_self(mapping.key, mapping)
                        _columns[mapping.key] = mapping.index
                        break
        self.columns = _columns

    @property
    def success(self):
        return len(self.columns.keys()) == len(self.fields)

    @property
    def schema(self):
        return self.columns
