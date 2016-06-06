
from datetime import datetime
from tempfile import TemporaryFile
from xml.etree import ElementTree

from ..ldritems.ldrpath import LDRPath

__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class ArchiveFitsModifier(object):
    """
    The ArchiveFitsModifier is the class for modifiying fits records for ingestion
    into the ldr archive
    """
    def __init__(self, record, location_string):
        """initializes an ArchiveFitsModifier object to be ready to modify the record
        
        __Args__
        1. record (LDRItem): an LDR file-like object pointing to a FITS xml record
        2. location_string (str): a string representing a location to save the modified
        xml record
        """
        self.record = record
        self.location_string = location_string

    def modify_record(self):
        """returns an XML node with a modified filePath and lastmodified 
        element text
        """
        root_of_xml_object = self.record.getroot()
        filePath = root_of_xml_object.find(
            '{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}fileinfo/' +
            '{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}filepath')
        filePath.text = self.location_string
        lastmodified = root_of_xml_object.find(
            '{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}fileinfo/' +
            '{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}lastmodified')
        if lastmodified:
            lastmodified.text = datetime.now().isoformat()
        return self.record

    def get_location_string(self):
        """returns the location_string data attribute
        """
        return self._location_string

    def set_location_string(self, value):
        """sets the location_string data attribute
        """
        self._location_string = value

    def get_record(self):
        """returns the record data attribute
        """
        return self._record

    def set_record(self, value):
        """sets the record data attribute value
        
        __Args__
        1. value (LDRItem): a file-like object pointing to a FITS record
        """
        with TemporaryFile() as tempfile:
            with value.open('rb') as read_file:
                while True:
                    buf = read_file.read(1024)
                    if buf:
                        tempfile.write(buf)
                    else:
                        break
            tempfile.seek(0)
            self._record = ElementTree.parse(tempfile)

    record = property(get_record, set_record)
    location_string = property(get_location_string, set_location_string)
