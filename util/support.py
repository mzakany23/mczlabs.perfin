import hashlib
import re

def strip_white(string):
    return re.sub(r'\s+', '', string)

def generate_specific_key(key_string):
    """support function"""
    key_string = key_string.encode('utf-8')
    hash_object = hashlib.sha256(key_string)
    hex_dig = hash_object.hexdigest()
    return hex_dig
