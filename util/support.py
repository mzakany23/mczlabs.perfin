import hashlib
import re


def shorten_filename(string, word):
    regex = r'{}'.format(word.lower())
    found = re.search(regex, string.lower())
    return found.group() if found else string
    

def strip_white(string):
    return re.sub(r'\s+', '', string)


def generate_specific_key(key_string):
    """support function"""
    key_string = key_string.encode('utf-8')
    hash_object = hashlib.sha256(key_string)
    hex_dig = hash_object.hexdigest()
    return hex_dig
