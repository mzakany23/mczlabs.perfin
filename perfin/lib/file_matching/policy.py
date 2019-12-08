from .base import Base
from .mapping import *




class FilePolicyManager(Base):
    def __init__(self, *args, **kwargs):
        super(FilePolicyManager, self).__init__(*args, **kwargs)
        self.policy = kwargs.get('policy')
        self._policies = [FilePolicy(domain=item['key'], policy_body=item) for item in self.policy]

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
        self.policy_trim = self.policy_body.get('trim')
        
        self.mapping = Mapping(
            header=self.policy_body['header'], 
            columns=self.policy_body['fields']
        )

    @property
    def __info__(self):
        self.header_print('File Policy')
        self.pretty_print(self.to_dict())
    
    @property
    def serialized_header(self):
        return '{}'.format(self.policy_header)
    
    def to_dict(self):
        return {self.domain : self.policy_body}
    