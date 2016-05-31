
class PremisRestrictionsExtraction(object):
    def __init__(self, record):
        self.record = record
        self.restrictions = []

    def extract_restrictions(self):
        self.record.get_rights()

    def get_record(self):

        for right in self.record.get_rights():
            for restriction in right.get_restrictions():
                restrictionCode = restriction.get_restrictionCode()
                self.restrictions.append(restrictionCode)
        return self.restrictions

    def set_record(self, value):
        if getattr(self,'_record', None):
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
