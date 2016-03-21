from re import compile as re_compile
from csv import DictReader


class REs(object):
    class FilePathPatterns(object):
        trailing_numbers = re_compile('[0-9]+$')
        fits_filepath = re_compile('\.fits\.xml$')
        premis_filepath = re_compile('\.premis\.xml$')
        presform_filepath = re_compile('\.presform$|\.presform\.[\w]{3}$')
        presform_filepath_just_files = re_compile('\.presform\.[\w]{3}$')
        presform_filepath_just_files = re_compile('\.presform\.[\w]{3}$')

    class FromCSV(object):
        def __init__(self, csv):
            with open(csv, 'r') as f:
                reader = DictReader(f)
                for row in reader:
                    setattr(self, row['name'], re_compile(row['pattern']))
