from .support import strip_white
from dateutil.parser import parse


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
        