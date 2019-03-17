import json
from .support import strip_white, shorten_filename, word_in_string
from fuzzywuzzy import fuzz
import operator
from .exceptions import MalformedParams
from dateutil.parser import parse


class Base(object):

    def __init__(self, *args, **kwargs):
        self.init_kwargs = kwargs 

    @property
    def __info__(self): 
        print('class {}'.format(self.__class__))        

    def validate(self, keys):
        kwargs = self.init_kwargs
        if isinstance(kwargs, dict):
            kwarg_keys = list(kwargs.keys())
            listed = [key for key in keys if kwargs.get(key) or kwargs.get(key) == 0]
            if len(kwarg_keys) != len(listed):
                raise MalformedParams('{} {} {}'.format(self.__class__.__name__, kwarg_keys, listed))

    def pretty_print(self, msg):
        print(json.dumps(msg, indent=4))

    def header_print(self, msg):
        print('---------------------------------------------')
        print(msg)
        print('---------------------------------------------')
        

class MappingType(Base):
    def __init__(self, *args, **kwargs):
        super(MappingType, self).__init__(*args, **kwargs)
        self.validate(['key', 'index', 'boost'])
        self.boost_match = False 
        self.key = kwargs.get('key')
        self.index = kwargs.get('index')
        self.boost = kwargs.get('boost')

        boost_index = self.boost.get(self.key)

        if boost_index == self.index:
            self.boost_match = True
    
    @property
    def __info__(self):
        self.header_print('Mapping info')
        return {
            'type' : self.key,
            'index' : self.index,
            'matches_boost' : self.matches
        }

    @property
    def matches(self):
        return self.boost_match

    

class Mapping(Base):
    _types = [
        'date',
        'description',
        'amount',
        'type'
    ]

    def __init__(self, *args, **kwargs):
        super(Mapping, self).__init__(*args, **kwargs)
        self.validate(['fields', 'boost'])
        self.fields = kwargs.get('fields')
        self.boost = kwargs.get('boost')
        self.calculate()

    @property
    def __info__(self):
        self.header_print('Schema')
        return self.pretty_schema

    def is_date(self, item):
        return word_in_string('date', item)

    def is_type(self, item):
        return word_in_string('type', item)

    def is_description(self, item):
        return word_in_string('description', item) or word_in_string('transaction', item)

    def is_amount(self, item):
        return word_in_string('amount', item)

    def get_type(self, index, key):
        return MappingType(index=index, key=key, boost=self.boost)
        
    def calculate(self):
        for index, field in enumerate(self.fields):
            for _type in self._types:
                attr = 'is_{}'.format(_type)
                found = getattr(self, attr)(field)
                if found:
                    setter = self.get_type(index, found)
                    setattr(self, _type, setter)
                    break

    @property
    def types(self):
        return [getattr(self, _type) for _type in self._types]
    
    @property
    def schema(self):
        _schema = {}
        for _type in self.types:
            _schema[_type.key] = _type.info
        return _schema

    @property
    def pretty_schema(self):
        self.pretty_print(self.schema)

    @property 
    def matches_boost(self):
        match_length = len([_type for _type in self.types if _type.matches])
        boost_length = len(list(self.boost.keys()))
        return match_length == boost_length

    

class FilePolicyManager(Base):
    def __init__(self, *args, **kwargs):
        super(FilePolicyManager, self).__init__(*args, **kwargs)
        self.validate(['policy'])
        self.policy = kwargs.get('policy')
        self._policies = [FilePolicy(domain=k, policy_body=v) for k, v in self.policy.items()]

    @property
    def __info__(self):
        lookup = {}
        for policy in self._policies:
            lookup.update(policy.to_dict())
        self.header_print('Policies')
        self.pretty_print(lookup)

    @property
    def policies(self):
        return self._policies
    

class FilePolicy(Base):
    def __init__(self, *args, **kwargs):
        super(FilePolicy, self).__init__(*args, **kwargs)
        self.validate(['domain', 'policy_body'])
        self.domain = kwargs.get('domain')
        self.policy_body = kwargs.get('policy_body')
        self.policy_header = self.policy_body['header']

    @property
    def serialized_header(self):
        return '{}'.format(self.policy_header)

    @property
    def __info__(self):
        self.header_print('File Policy')
        self.pretty_print(self.to_dict())
    
    def to_dict(self):
        return {self.domain : self.policy_body}
    

class FileMatchManager(Base):
    _matches = {}
    
    @property
    def __info__(self):
        self.header_print('Matches sort in descending order')
        print('matches length: {}'.format(len(self._matches)))
        item = [(item.domain, item.total_score) for item in self.descending]
        self.pretty_print(item)

    def add(self, file):
        total_score = file.total_score
        self._matches[total_score] = file 

    @property
    def matches(self):
        return sorted(self._matches.items(), key=operator.itemgetter(0), reverse=True)
    
    @property 
    def top(self):
        score = self.descending
        return score[0] if len(score) > 0 else None

    @property
    def descending(self):
        return [item[1] for item in self.matches]



class FileMatch(Base):
    base_stat_fields = [
        'header_score',
        'filename_score',
    ]

    def __init__(self, *args, **kwargs):
        super(FileMatch, self).__init__(*args, **kwargs)
        empty = kwargs.get('empty')
        if not empty:
            self.validate(['domain', 'filename', 'headers'])

            self.domain = kwargs.get('domain')
            self._filename = kwargs.get('filename')
            self.filename = shorten_filename(self._filename, self.domain)
            self.headers = kwargs.get('headers')
            
            self._header_score = self.get_score(self.headers[0], self.headers[1])
            self._filename_score = self.get_score(self.domain.lower(), self.filename)

            self.header_score = self._header_score
            self.filename_score = self._filename_score
            
            if self.header_score == 100:
                self.header_score += 50

            if  self.filename_score == 100:
                self.filename_score += 50
            
            elif self.filename_score > 80:
                self.filename_score += 10
            
            elif self.filename_score <= 50:
                self.header_score -= 100
            else:
                self.header_score -= 30
                self.filename_score -= 50

    @property
    def __info__(self):
        item = {
            'header_score' : self.header_score, 
            'filename_score' : self.filename_score, 
            'total' : self.total_score
        }
        self.header_print('top matches in descending order')
        print(json.dumps(item, indent=4))

    @property
    def total_score(self):
        return sum([getattr(self, key) for key in self.base_stat_fields])
    

    def get_score(self, one, two):
        return fuzz.ratio(one, two)

    
class FileAnalyzer(Base):
    def __init__(self, *args, **kwargs):
        super(FileAnalyzer, self).__init__(*args, **kwargs)
        self.validate(['header', 'filename', 'policy'])
        self.policy = kwargs.get('policy')
        self.min_required_score = kwargs.get('min_required_score', 70)
        self.header = kwargs.get('header', [])
        self.filename = kwargs.get('filename', [])
        self.policy_manager = FilePolicyManager(policy=self.policy)
    
    @property
    def serialized_header(self):
        return '{}'.format(self.header)
        
    @property
    def top_match(self):
        matches = self.calculate_matches()
        top_match = matches.top
        
        return (
            top_match 
            if top_match.total_score > self.min_required_score 
            else FileMatch(empty=True)
        )
            
        
    def calculate_matches(self):
        matches = FileMatchManager()
        # wtf looping twice on second run?
        # why is it double looping?

        for policy in self.policy_manager.policies:
            file_match = FileMatch(
                domain=policy.domain,
                filename=self.filename,
                headers=[policy.serialized_header, self.serialized_header],
            )
            matches.add(file_match)
        return matches


class RowFactory(object):
    def __init__(self, doc_id, account_types, header_key, row):
        account = account_types[header_key]
        self.fields = account["fields"].keys()
        self.doc_id = doc_id
        self.account_name = account["name"]
        
        for field_key in self.fields:
            index = account["fields"][field_key]
            setattr(self, field_key, row[index])
        
        if hasattr(self, 'date'):
            item = parse(self.date)
            self.date = item.strftime("%Y-%m-%d")
        
        if "trim" in account:
            self.trim_key = account["trim"]["field"]
            self.trim_value = account["trim"]["value"]
        else:
            self.trim_key = False

        if self.amount:
            try:
                self.amount = float(self.amount)    
            except:
                for item in row:
                    try:
                        _item = float(item)
                        self.amount = _item
                        break
                    except:
                        pass
                        
    @property
    def _key(self):
        return strip_white(self.description.lower())

    def get_doc(self):
        doc = {
            "_id" : self.doc_id,
            "document" : {
                "account" : self.account_name
            }
        }

        if self.trim_key:
            field = getattr(self, self.trim_key)
            doc["_group"] = field[:self.trim_value]

        for field in self.fields:
            doc["document"][field] = getattr(self, field)

        return doc
        