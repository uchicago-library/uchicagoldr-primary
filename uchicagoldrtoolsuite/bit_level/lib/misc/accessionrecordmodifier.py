
import json
from tempfile import TemporaryFile

from hierarchicalrecord.hierarchicalrecord import HierarchicalRecord

from ..auditors.abc.auditor import Auditor
from ..ldritems.abc.ldritem import LDRItem

__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class AccessionRecordModifier(object):
    """The AccessionRecordModifier is meant to modify an accession record in an archive
    structure with the information required for an accession to be completely ingested
    into the ldr.
    """
    def __init__(self, subject):
        """initializes an AccessionRecordModifier

        __Args__
        1. subject (LDRItem) : some LDR file-like object that contains JSON
        data that is a valid accession record
        """
        self.record = subject

    def add_restriction_info(self, restriction_list):
        """takes a list of strings that are meant to be restrictions and adds them to
        the record's Restrictions field
        """
        restrictionfields = [x for x in self.record.keys() if 'Restriction' in x]
        if restrictionfields:
            orig = set(self.record['Restrictions'])
        else:
            orig = set([])
        for n_restriction in restriction_list:
            orig.add(n_restriction)

        for n_item in orig:
            self.record.add_to_field('Restrictions', n_item)

    def write(self, file_location):
        """writes the contents of the record to the file_location specified

        __Args__
        1. file_location (str): a string representing a path to a location
        on-disk to save the record
        """
        jsonified_hrecord = self.record.toJSON()
        with open(file_location, 'wb') as writing_file:
            writing_file.write(bytes(jsonified_hrecord.encode('utf-8')))

    def get_record(self):
        """returns the record data attribute
        """
        return self._record

    def set_record(self, value):
        """sets the record data attribute value

        _Args__
        1. value (LDRItem): the location on-disk of an accession record
        """
        if isinstance(value, LDRItem):
            with TemporaryFile() as tempfile:
                with value.open('rb') as read_file:
                    while True:
                        buf = read_file.read(1024*1000*100)
                        if buf:
                            tempfile.write(buf)
                        else:
                            break
                    tempfile.seek(0)
                    hrecord = HierarchicalRecord()
                    data = tempfile.read().decode('utf-8')
                    data = json.loads(data)
                    hrecord.set_data(data)
                    self._record = hrecord
        else:
            raise ValueError(
                "AccessionRecordAuditor can only take an LDRItem as subject")


    record = property(get_record, set_record)
