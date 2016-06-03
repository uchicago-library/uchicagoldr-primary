
from tempfile import TemporaryFile

from xml.etree import ElementTree

from .abc.auditor import Auditor
from .errorpackager import ErrorPackager

__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class FitsAuditor(Auditor):
    """The FitsAuditor class is meant to audit a fits record
    for usefulness to the LDR
    """
    def __init__(self, subject):
        self.subject = subject
        self.errorpackager = ErrorPackager()

    def audit(self):
        """returns a boolean value

        This function checks that hte xml metadata in a given FITS record
        file contains a filePath element and a metadata element
        """
        root_of_xml_object = self.subject
        filePath = root_of_xml_object.find(
            '{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}fileinfo/' +
            '{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}filepath')
        metadata = root_of_xml_object.find(
            '{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}metadata')
        if metadata is None:
            self.errorpackager.add(
                "fits",
                "fits record for is missing a metadata node")
        if filePath is None:
            self.errorpackager.add(
                "fits",
                "fits is missing a filePath element")
        if len(self.errorpackager.errors) > 0:
            return False
        return True

    def show_errors(self):
        """returns a list of the errors found in an audit of the subject
        """
        return self.errors.display()

    def get_subject(self):
        """returns the subject data attribute
        """
        return self._subject

    def set_subject(self, value):
        """sets the subject data attribute_string

        It transforms the value passed into an ElementTree object if possible.

        __Args__
        1. value (LDRPath): an LDR file-like object pointing to to a
        FITS metadata record
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
                xmldata_string = tempfile.read().decode('utf-8')
                self._subject = ElementTree.fromstring(xmldata_string)

    def get_errorpackager(self):
        """returns the errorpackager delegate for the auditor
        """
        return self._errorpackager

    def set_errorpackager(self, value):
        """sets the errorpackager data attribute
        """
        self._errorpackager = value

    subject = property(get_subject, set_subject)
    errorpackager = property(get_errorpackager, set_errorpackager)
