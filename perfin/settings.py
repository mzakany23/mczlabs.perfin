import hashlib
import uuid

DATE_FMT = "%Y-%m-%d"


def generate_better_key(self):
    hash_object = hashlib.sha256(str(uuid.uuid4()).encode("utf8"))
    hex_dig = hash_object.hexdigest()
    return hex_dig


def generate_specific_key(self, *args):
    key_string = "".join([*args]).encode("utf-8")
    hash_object = hashlib.sha256(key_string)
    hex_dig = hash_object.hexdigest()
    return hex_dig
