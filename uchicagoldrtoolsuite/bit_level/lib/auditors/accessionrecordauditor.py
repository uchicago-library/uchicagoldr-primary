
import json
from tempfile import TemporaryFile

from hierarchicalrecord.hierarchicalrecord import HierarchicalRecord

from .abc.auditor import Auditor
from ..ldritems.abc.ldritem import LDRItem
from .errorpackager import ErrorPackager


class AccessionRecordAuditor(Auditor):
    def __init__(self, subject):
        self.subject = subject
        self.errorpackager = ErrorPackager()
        self.minimum_required_fields = [
            'Accession Number',
            'Organization Name'
            'Summary',
            'Collection Title',
            'EADID',
            'Rights',
            'Restrictions',
            'RestrictionComments',
            'Origin',
            'Access',
            'Discover',
            'Administrative Comments',
            'Access Description'
        ]

    def get_subject(self):
        return self._subject

    def audit(self):
        fields_in_record = self.subject.keys()
        check_field_existence = [
            x for x in fields_in_record if x not in
            self.minimum_required_fields
        ]
        if len(check_field_existence) > 0:
            self.errorpackager.add("accessionrecord",
                            "accession record is missing " +
                            "the following fields " +
                            "{}".format(', '.join(check_field_existence)))
        if len(self.errorpackager.errors) > 0:
            return False
        else:
            return True

    def show_errors(self):
        return self.errors.display()

    def set_subject(self, value):
        if isinstance(value, LDRItem):
            with TemporaryFile() as tempfile:
                with value.open('rb') as read_file:
                    while True:
                        buf = read_file.read(1024)
                        if buf:
                            tempfile.write(buf)
                        else:
                            break
                    tempfile.seek(0)
                    hrecord = HierarchicalRecord()
                    data = tempfile.read().decode('utf-8')
                    data = json.loads(data)
                    hrecord.data_object = data
                    self._subject = hrecord
        else:
            raise ValueError(
                "AccessionRecordAuditor can only take an ldritem as subject")

    def get_errorpackager(self):
        return self._errorpackager

    def set_errorpackager(self, value):
        self._errorpackager = value

    subject = property(get_subject, set_subject)
    errorpackager = property(get_errorpackager, set_errorpackager)
