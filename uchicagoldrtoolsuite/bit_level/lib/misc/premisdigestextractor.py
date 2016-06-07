
from collections import namedtuple
from tempfile import TemporaryFile

from pypremis.lib import PremisRecord

from ..ldritems.abc.ldritem import LDRItem

__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class PremisDigestExtractor(object):
    """The PremisDigestExtractor is meant to pull digest information from
    a particular PREMIS record for addition elsewhere in the system.
    """
    def __init__(self, record):
        """initializes a PremisDigestExtractor
        
        __Args__
        
        1. record (LDRITem): an LDR file-like object pointing to a PREMIS record for a 
        particular resource, 
        """
        self.record = record

    def extract_digests(self):
        """returns a list of named tuple called digests data which has a data attribute
        that is a list of named tuple objects called "digestdata that have a algo attribute and 
        a digest attribute. The algo attribute is the hashing algorithm used to derive the value
        in the digest attribute.
        """
        output = namedtuple("digests", "data")([])
        for obj in self.record.get_object_list():
            for characteristic in obj.get_objectCharacteristics():
                for fixity in characteristic.get_fixity():
                    digest = fixity.get_messageDigest()
                    digestAlgo = fixity.get_messageDigestAlgorithm()
                    digest_data = namedtuple("digestdata", "algo digest")
                    record = digest_data(digestAlgo, digest)
                    output.data.append(record)
        return output

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
                        buf = read_file.read(1024)
                        if buf:
                            tempfile.write(buf)
                        else:
                            break
                tempfile.seek(0)
                self._record = PremisRecord(frompath=tempfile)

    record = property(get_record, set_record)
