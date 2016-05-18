from os.path import abspath, join, split, exists
from pypremis.lib import PremisRecord

from tempfile import TemporaryFile

from .archive import Archive
from .abc.auditor import Auditor
from .errorpackager import ErrorPackager
from .ldrpath import LDRPath


class ArchiveAuditor(Auditor):
    def __init__(self, source_directory, the_subject):
        self.source = source_directory
        self.subject = the_subject
        self.errors = ErrorPackager()

    def get_subject(self):
        return self._subject

    def set_subject(self, value):
        if isinstance(value, Archive):
            self._subject = value
        else:
            raise ValueError("ArchiveAuditor can only audit a subject " +
                             "that is an Archive instance")

    def audit(self):
        return (True, None)
        if getattr(self.subject, 'accessionrecord_list', None) == []:
            self.errors.add("record", "missing accession record")

        for n_segment in self.subject.segment_list:
            for n_msuite in n_segment.materialsuite_list:
                with TemporaryFile() as tempfile:
                    with n_msuite.premis.open('rb') as reading_file:
                        while True:
                            buf = reading_file.read(1024)
                            if buf:
                                tempfile.write(buf)
                            else:
                                break
                    tempfile.seek(0)
                    precord = PremisRecord(frompath=tempfile)

                    for obj in precord.get_object_list():
                        for storage in obj.get_storage():
                            if not storage.get_contentLocation():
                                self.errors.add("premis",
                                                "no contentLocation element found")
                        fixities = []
                        for characteristic in obj.get_objectCharacteristics():
                            for fixity in characteristic.get_fixity():
                                fixities.append(fixity)
                        if len(fixities) == 2:
                            pass
                        else:
                            self.errors.add("premis",
                                            "wrong number of fixities." +
                                            " There should be 2")
                if not getattr(n_msuite, 'premis', None):
                    self.errors.add("file",
                                    "no premis record for file {}".format(
                                        n_msuite.content.item_name))
                if getattr(n_msuite, 'presform_list', None) != None:
                    for n_presform in n_msuite.presform_list:
                        if not getattr(n_presform, 'premis', None):
                            self.errors.add("file",
                                            "no premis record for file {}".format(
                                                n_presform.content.item_name))
        if self.errors.numErrors != 0:
            return (False, self.errors)
        else:
            return (True, None)

    def show_errors(self):

        return self.errors.display()

    subject = property(get_subject, set_subject)
