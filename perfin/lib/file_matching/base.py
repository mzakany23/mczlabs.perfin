import json
from .exceptions import MalformedParams

class Base(object):

    def __init__(self, *args, **kwargs):
        self.init_kwargs = kwargs 

    @property
    def __info__(self): 
        print('class {}'.format(self.__class__))        

    def set_self(self, key, value):
        setattr(self, key, value)
    
    def has(self, attr):
        return hasattr(self, attr)
        
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
    
    def raise_malformed(self, **kwargs):
        msg = kwargs.get('message', 'malformed')
        raise MalformedParams(msg)