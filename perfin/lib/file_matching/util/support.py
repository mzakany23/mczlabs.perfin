import csv
import hashlib
import uuid
import re

from datetime import datetime

from dateutil.parser import parse


def word_in_string(word, string):
    regex = r'{}'.format(word.lower())
    found = re.search(regex, string.lower())
    return found.group() if found else False


def shorten_filename(string, word):
    found = word_in_string(word, string)
    return found if found else string


def strip_white(string):
    return re.sub(r'\s+', '', string)


def generate_better_key():
    hash_object = hashlib.sha256(str(uuid.uuid4()).encode('utf8'))
    hex_dig = hash_object.hexdigest()
    return hex_dig


def generate_specific_key(key_string):
    key_string = key_string.encode('utf-8')
    hash_object = hashlib.sha256(key_string)
    hex_dig = hash_object.hexdigest()
    return hex_dig


def create_file_name(account, from_date, to_date):
    key = generate_better_key()[0:10]
    return '{}____{}-{}.key={}'.format(account, from_date, to_date, key)


def _generate_new_file_name(old_filename, from_date, to_date):
    _name = old_filename.lower()

    if 'export' in _name or 'fifth_third' in _name or '53' in _name:
        file_name = 'fifth_third'
    elif 'chase' in _name:
        file_name = 'chase'
    elif 'capone' in _name:
        file_name = 'capital_one'
    else:
        file_name = 'capital_one'

    new_file_name_name = create_file_name(file_name, from_date, to_date)

    return new_file_name_name, file_name


def generate_new_file_name(old_filename, header, rows):
    dates = []

    for row in rows:
        date_col = None

        for i, col in enumerate(header):
            if 'date' in col.lower():
                date_col = i
                break

        if not rows:
            continue
        elif len(rows) == 1:
            row = rows[0]
            rows = [row, row]

        for row in rows:
            date = row[date_col].replace('/', '-')
            date = parse(date).strftime('%Y-%m-%d')
            dates.append(date)

    if dates:
        dates.sort(key=lambda date: datetime.strptime(date, '%Y-%m-%d'))

        from_date, to_date = dates[0], dates[-1]

        return _generate_new_file_name(old_filename, from_date, to_date)
    return None, None
