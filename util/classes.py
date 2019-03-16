from .support import strip_white, shorten_filename
from fuzzywuzzy import fuzz
import operator
from dateutil.parser import parse


class MalformedParams(Exception):
    pass


class Base(object):
    def __init__(self, *args, **kwargs):
        self.init_kwargs = kwargs 

    def validate(self, keys):
        kwargs = self.init_kwargs
        if isinstance(kwargs, dict):
            kwarg_keys = list(kwargs.keys())
            listed = [key for key in keys if kwargs.get(key)]
            if len(kwarg_keys) != len(listed):
                raise MalformedParams('{} {} {}'.format(self.__class__.__name__, kwarg_keys, listed))
            

class FilePolicyManager(Base):
    def __init__(self, *args, **kwargs):
        super(FilePolicyManager, self).__init__(*args, **kwargs)
        self.validate(['policy'])
        self.policy = kwargs.get('policy')
        self._policies = [FilePolicy(domain=k, policy_body=v) for k, v in self.policy.items()]

    @property
    def policies(self):
        return self._policies
        

class FilePolicy(Base):
    def __init__(self, *args, **kwargs):
        super(FilePolicy, self).__init__(*args, **kwargs)
        self.validate(['domain', 'policy_body'])
        self.domain = kwargs.get('domain')
        policy_body = kwargs.get('policy_body')
        self.policy_header = policy_body['header']

    @property
    def serialized_header(self):
        return '{}'.format(self.policy_header)
    

class FileMatchManager(Base):
    _matches = {}
    
    def add(self, file):
        total_score = file.total_score
        self._matches[total_score] = file 

    @property
    def matches(self):
        return sorted(self._matches.items(), key=operator.itemgetter(0), reverse=True)
    
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
        self.validate(['domain', 'filename', 'headers'])
        
        self.domain = kwargs.get('domain')
        self.filename = shorten_filename(kwargs.get('filename'), self.domain)
        self.headers = kwargs.get('headers')
        
        self.header_score = self.get_score(self.headers[0], self.headers[1])
        self.filename_score = self.get_score(self.domain.lower(), self.filename)

        if self.header_score == 100:
            self.header_score += 50

        if self.filename_score == 100:
            self.filename_score += 50
        if self.filename_score > 80:
            self.filename_score += 10
        else:
            self.header_score -= 30
            self.filename_score -= 50
    
    @property
    def total_score(self):
        return sum([getattr(self, key) for key in self.base_stat_fields])
    
    def get_score(self, one, two):
        return fuzz.ratio(one, two)
        

class FileAnalyzer(Base):
    def __init__(self, *args, **kwargs):
        super(FileAnalyzer, self).__init__(*args, **kwargs)
        self.validate(['header', 'filename', 'policy'])

        policy = kwargs.get('policy')
        self.header = kwargs.get('header', [])
        self.filename = kwargs.get('filename', [])
        self.policy_manager = FilePolicyManager(policy=policy)

    @property
    def top_match(self):
        score = self.calculate_score() 
        return score[0] if len(score) > 0 else None

    @property
    def serialized_header(self):
        return '{}'.format(self.header)
    
    def calculate_score(self):
        matches = FileMatchManager()
        
        for policy in self.policy_manager.policies:
            file_match = FileMatch(
                domain=policy.domain,
                filename=self.filename,
                headers=[policy.serialized_header, self.serialized_header],
            )
            matches.add(file_match)
        return matches.descending


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
        