import csv
import hashlib
import re

from datetime import datetime

from dateutil.parser import parse

from s3fs.core import S3FileSystem


def word_in_string(word, string):
    regex = r'{}'.format(word.lower())
    found = re.search(regex, string.lower())
    return found.group() if found else False


def shorten_filename(string, word):
    found = word_in_string(word, string)
    return found if found else string


def strip_white(string):
    return re.sub(r'\s+', '', string)


def generate_specific_key(key_string):
    key_string = key_string.encode('utf-8')
    hash_object = hashlib.sha256(key_string)
    hex_dig = hash_object.hexdigest()
    return hex_dig


def create_file_name(account, from_date, to_date):
    return '{}____{}-{}'.format(account, from_date, to_date)


def open_and_yield_csv_row(s3, file_path):
    _open = s3.open(file_path, mode="r")
    with _open as f:
        rows = csv.reader(f)
        for row in rows:
            yield row


def get_s3_perfin_files():
    s3 = S3FileSystem(anon=False)
    s3_files = s3.ls('mzakany-perfin')

    for s3_file_name in s3_files:
        body = [row for row in open_and_yield_csv_row(s3, s3_file_name)]
        header = body[0]
        rows = body[1:]

        yield s3_file_name, header, rows


def generate_new_file_names(old_filename, header, rows):
    for row in rows:
        dates = []
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

        dates.sort(key=lambda date: datetime.strptime(date, '%Y-%m-%d'))

        from_date, to_date = dates[0], dates[-1]

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

        yield new_file_name_name, file_name
