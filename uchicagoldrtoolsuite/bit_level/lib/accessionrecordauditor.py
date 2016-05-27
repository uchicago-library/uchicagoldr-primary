
from tempfile import TemporaryFile

from hierarchicalrecord.hierarchicalrecord import HierarchicalRecord

from .abc.auditor import Auditor
from .abc.ldritem import LDRItem


class AccessionRecordAuditor(Auditor):
    def __init__(self, subject):
        self.subject = subject
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
            self.errors.add("accessionrecord",
                            "accession record is missing " +
                            "the following fields " +
                            "{}".format(', '.join(check_field_existence)))
        if len(self.errors.errors) > 0:
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
                    try:
                        self.subject = HierarchicalRecord(fromfile=tempfile)
                    except Exception as e:
                        raise e("AccessionRecordAuditor couldn't instantiate" +
                                " a HierarchicalRecord from the input")

        else:
            raise ValueError(
                "AccessionRecordAuditor can only take an ldritem as subject")
