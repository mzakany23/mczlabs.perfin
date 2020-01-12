import csv
import os
from ..lib.file_matching.config import TRIM_FIELD
from ..lib.file_matching.analyzer import FileAnalyzer


def get_files(directory, file_type):
    for path in os.listdir(directory):
        filename, file_extension = os.path.splitext(path)
        if file_extension.lower() == file_type:
            full_path = '{}/{}'.format(directory, path)
            yield full_path, filename, file_extension
                    