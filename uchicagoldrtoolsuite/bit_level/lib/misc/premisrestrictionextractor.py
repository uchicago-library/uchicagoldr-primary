
from tempfile import TemporaryFile

from pypremis.lib import PremisRecord

__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class PremisRestrictionsExtractor(object):
    """The PremisRestricitonExtractor is meant to be used to pull the restrictions set
    for a given resource in the PREMIS record so that the information can be used
    elsewhere in the system
    """

    def __init__(self, record):
        """initializes a PremisRestrictionExtractor object

        __Args__
        1. record (LDRItem): a file-like object pointing to a PREMIS record
        """
        self.record = record
        self.restrictions = []

    def extract_restrictions(self):
        """returns a list of strings that are all unique SPCL restrictions for a given resource
        pulled from the PREMIS record
        """
        for right in self.record.get_rights_list():
            for extension in right.get_rightsExtension():
                restrictions = extension.get_field('restriction')
                for restriction in restrictions:
                    codes = restriction.get_field('restrictionCode')
                    for code in codes:
                        self.restrictions.append(code)

        return self.restrictions

    def get_record(self):
        """returns the record data attribute
        """
        return self._record

    def set_record(self, value):
        """sets the record data attribute

        __Args__

        1. value (LDRItem): a file-like object pointing to a PREMIS record
        """
        if getattr(self,'_record', None):
            raise ValueError("record is already set")

        else:
            with TemporaryFile() as tempfile:
                with value.open('rb') as read_file:
                    while True:
                        buf = read_file.read(1024*1000*100)
                        if buf:
                            tempfile.write(buf)
                        else:
                            break
                tempfile.seek(0)
                self._record = PremisRecord(frompath=tempfile)

    record = property(get_record, set_record)
