from .config import BASE_POLICY
from .base import Base
from .policy import *
from .matching import *
from .scoring import ScoreResult




class FileAnalyzer(Base):
    def __init__(self, *args, **kwargs):
        super(FileAnalyzer, self).__init__(*args, **kwargs)

        self._policy = kwargs.get('policy', BASE_POLICY)
        self.header = kwargs.get('header', [])
        self.filename = kwargs.get('filename', [])
        self.policy_manager = FilePolicyManager(policy=self._policy)
        self.matches = self.calculate_matches()
    
    @property
    def __info__(self):
        self.matches.__info__
    
    @property
    def serialized_header(self):
        return '{}'.format(self.header)
        
    @property
    def score(self):
        return ScoreResult(match=self.matches.top)

    @property
    def top_match(self):
        return self.matches.top

    @property
    def account(self):
        return self.matches.top.domain

    @property
    def mapping(self):
        return self.top_match.policy.mapping
    
    @property
    def policy(self):
        return self.top_match.policy

    @property
    def fields(self):
        return self.mapping.fields
    
    def get_doc(self, row):
        policy = self.policy
        id_key = ",".join(row).replace(",", "").replace(" ", "")

        doc = {
            "_id" : generate_specific_key(id_key),
            "document" : {
                "account" : policy.domain
            }
        }

        for field in policy.mapping.fields:
            value = field.process(row)
            doc['document'][field.key] = value

        account = policy.policy_trim
        
        try:
            trim_key = account["field"]
            trim_value = account["value"]
        except:
            trim_key, trim_value = False, False

        if trim_key and trim_value:
            doc["_group"] = doc['document'][trim_key][:trim_value]
        return doc

    def calculate_matches(self):
        matches = FileMatchManager()
        
        for policy in self.policy_manager.policies:
            file_match = FileMatch(
                policy=policy,
                header=self.header,
                filename=self.filename,
            )
            matches.add(file_match)
        return matches