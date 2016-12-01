
import json
from tempfile import TemporaryFile

from hierarchicalrecord.hierarchicalrecord import HierarchicalRecord

from ..ldritems.abc.ldritem import LDRItem
from .abc.auditor import Auditor
from .errorpackager import ErrorPackager

__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class AccessionRecordAuditor(Auditor):
    """AccessionRecordAuditor is an auditor responsible for checking
    that an accession record is useful for the LDR
    """
    def __init__(self, subject):
        """instantiates an AccessionRecordAuditor

        __Args__
        1. subject (LDRItem): the LDR file-like object pointing to an
        accession record
        """
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

    def audit(self):

        fields_in_record = self.subject.keys()
        check_field_existence = [
            x for x in fields_in_record if x not in
            self.minimum_required_fields
        ]
        if len(check_field_existence) > 0:
            self.errorpackager.add(
                "accessionrecord",
                "accession record is missing " +
                "the following fields " +
                "{}".format(', '.join(check_field_existence)))
        if len(self.errorpackager.errors) > 0:
            return False
        else:
            return True

    def show_errors(self):
        """returns the errors found in an audit
        """
        return self.errors.display()

    def get_subject(self):
        """returns the subject data attribute
        """
        return self._subject

    def set_subject(self, value):
        """sets the subject data attribute_string

        It takes an LDRItem and sets a HierarchicalRecord
        containing the data from that accession record
        as the subject data attribute

        __Args__
        1. value (LDRItem): a file-like object pointing
        """
        if isinstance(value, LDRItem):
            with TemporaryFile() as tempfile:
                with value.open('rb') as read_file:
                    while True:
                        buf = read_file.read(1024 * 1000 * 100)
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
        """returns the errorpackager data  attribute
        """
        return self._errorpackager

    def set_errorpackager(self, value):
        """sets the errorpackager data attribute
        """
        self._errorpackager = value

    subject = property(get_subject, set_subject)
    errorpackager = property(get_errorpackager, set_errorpackager)
