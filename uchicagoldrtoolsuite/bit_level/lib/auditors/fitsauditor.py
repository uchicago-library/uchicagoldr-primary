
from tempfile import TemporaryFile

from xml.etree import ElementTree

from .abc.auditor import Auditor
from .errorpackager import ErrorPackager
from ..ldritems.abc.ldritem import LDRItem


class FitsAuditor(Auditor):
    def __init__(self, subject):
        self.subject = subject
        self.errorpackager = ErrorPackager()

    def audit(self):
            root_of_xml_object = self.subject
            filePath = root_of_xml_object.find(
                '{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}fileinfo/'+
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
            else:
                return True

    def show_errors(self):
        return self.errors.display()

    def get_subject(self):
        return self._subject

    def set_subject(self, value):
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
        return self._errorpackager

    def set_errorpackager(self, value):
        self._errorpackager = value

    subject = property(get_subject, set_subject)
    errorpackager = property(get_errorpackager, set_errorpackager)
