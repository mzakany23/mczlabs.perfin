from .support import strip_white


def process_lookup(row_factory, lookup, keys, length=12):
    """
        PARAMS
            process_lookup(
                row_object, 
                TRANSACTION_TYPES, 
                keys)
    """
    # look here!
    # this is the main method that parses and sets a doc

    doc = row_factory.get_doc()
    for key in keys:
        _key = strip_white(key)
        kl = len(_key)
        if (kl > length): 
            length = kl
        lookup_key = _key[0:length].lower()
        if lookup_key in row_factory._key:
            for k, v in lookup[key].items():
                doc["document"][k] = v
                        
    # here! this is what happens when
    # doc does not contain what you want
    # i.e. set defaults
    # must make sure doc has all these fields!
    # "ELECTRONIC IMAGE" : {
    #     "name" : "CHECK",
    #     "category" : "FINANCIAL",
    #     "organization" : "FIFTH_THIRD_BANK",
    #     "expense_type" : "VARIABLE"    
    # },

    if "name" not in doc["document"]:
        doc["document"]["name"] = "OTHER"
        
    if "category" not in doc["document"]:
        doc["document"]["category"] = "OTHER"

    return doc