from tempfile import TemporaryFile

from pypremis.lib import PremisRecord

from .abc.auditor import Auditor
from .errorpackager import ErrorPackager


class PremisAuditor(Auditor):
    def __init__(self, subject):
        self.subject = subject
        self.errors = ErrorPackager()

    def audit(self):
        record_events = self.subject.get_event_list()
        if len(record_events) < 1:
            self.errors.add(
                "premis",
                "premis record for {} ".format(self.subject.filepath) +
                " has no events.")
        for obj in self.subject.get_object_list():
            for storage in obj.get_storage():
                if not storage.get_contentLocation():
                    self.errors.add(
                        "premis",
                        "premis record for {}".format(self.subject.filepath) +
                        " is missing a contentLocation")
            for characteristic in obj.get_objectCharacteristics():
                fixities = [characteristic.get_fixity()]
                if len(fixities) == 0:
                    self.errors.add(
                        "premis",
                        "premis record for {}".format(
                            self.subject.filepath) +
                        " is missing fixity information")
        if len(self.errors.errors) > 0:
            return False
        else:
            return True

    def show_errors(self):
        return self.errors.display()

    def get_subject(self):
        return self._subject

    def set_subject(self, value):
        with TemporaryFile() as tempfile:
            with value.open('rb') as read_file:
                while True:
                    buf = read_file.read(1024)
                    if buf:
                        tempfile.write(buf)
                    else:
                        break
                tempfile.seek(0)
                self._subject = PremisRecord(frompath=tempfile)

    def get_errorpackager(self):
        return self._errorpackager

    def set_errorpackager(self, value):
        self._errorpackager = value

    subject = property(get_subject, set_subject)
    errorpackager = property(get_errorpackager, set_errorpackager)
