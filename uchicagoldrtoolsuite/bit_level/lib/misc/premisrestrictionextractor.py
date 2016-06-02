
from tempfile import TemporaryFile

from pypremis.lib import PremisRecord


class PremisRestrictionsExtractor(object):
    def __init__(self, record):
        self.record = record
        self.restrictions = []

    def extract_restrictions(self):

        for right in self.record.get_rights_list():
            for extension in right.get_rightsExtension():
                restrictions = extension.get_field('restriction')
                for restriction in restrictions:
                    codes = restriction.get_field('restrictionCode')
                    for code in codes:
                        self.restrictions.append(code)

        return self.restrictions

    def get_record(self):
        return self._record

    def set_record(self, value):
        if getattr(self,'_record', None):
            print("hi")
            raise ValueError("record is already set")

        else:
            with TemporaryFile() as tempfile:
                with value.open('rb') as read_file:
                    while True:
                        buf = read_file.read(1024)
                        if buf:
                            tempfile.write(buf)
                        else:
                            break
                tempfile.seek(0)
                self._record = PremisRecord(frompath=tempfile)

    record = property(get_record, set_record)
