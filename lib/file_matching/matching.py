from .base import Base 
from .util.support import *
from fuzzywuzzy import fuzz
import operator




class FileMatchManager(Base):
    def __init__(self):
        self._matches = {}
    
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
    def __init__(self, *args, **kwargs):
        super(FileMatch, self).__init__(*args, **kwargs)
        self.validate(['policy', 'header', 'filename'])
        self.base_stat_fields = [
            'header_score',
            'filename_score',
        ]
        self.policy_header = kwargs.get('header')
        self.policy = kwargs.get('policy')
        self.domain = self.policy.domain
        self._filename = kwargs.get('filename')
        self.filename = shorten_filename(self._filename, self.domain)
        self.headers = [self.policy.serialized_header, self.serialized_header]
        
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
        self.pretty_print(item)

    @property
    def total_score(self):
        return sum([getattr(self, key) for key in self.base_stat_fields])
    
    @property
    def serialized_header(self):
        return '{}'.format(self.policy_header)

    def get_score(self, one, two):
        return fuzz.ratio(one, two)
