from tempfile import TemporaryFile

from pypremis.lib import PremisRecord

from .abc.auditor import Auditor
from .errorpackager import ErrorPackager

__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class PremisAuditor(Auditor):
    """The PremisAuditor class is meant to audit a premis record
    for usefulness to the LDR
    """

    def __init__(self, subject):
        """returns an instance of a PremisAuditor

        __Args__
        1. subject (Structure): the PremisRecord that needs to audited
        """
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
        """returns the subject data attribute of the PremisAuditor
        """
        return self._subject

    def set_subject(self, value):
        """sets the subject data attribute of the PremisAuditor

        This function opens a temporary file and the value parameter
        and writes the bytes content of the value parameter into a
        temporary file then sets the subject data attribute as an
        instance of PremisRecord containing the data in the
        temporary file

        __Args__
        1. value (LDRPath): the LDR file-like object that points
        to a serialized premis record
        """
        with TemporaryFile() as tempfile:
            with value.open('rb') as read_file:
                while True:
                    buf = read_file.read(1024 * 1000 * 100)
                    if buf:
                        tempfile.write(buf)
                    else:
                        break
                tempfile.seek(0)
                self._subject = PremisRecord(frompath=tempfile)

    def get_errorpackager(self):
        """returns the errorpackager of the auditor
        """
        return self._errorpackager

    def set_errorpackager(self, value):
        """sets the errorpackager delegate for the auditor
        """
        self._errorpackager = value

    subject = property(get_subject, set_subject)
    errorpackager = property(get_errorpackager, set_errorpackager)
