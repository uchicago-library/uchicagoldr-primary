
from tempfile import TemporaryFile
from xml.etree import ElementTree

from .abc.ldritem import LDRItem


class ArchiveFitsModifier(object):
    def __init__(self, record, location_string):
        self.record = record
        self.location_string = location_string

    def modify_record(self):
        root_of_xml_object = self.subject.getroot()
        filePath = root_of_xml_object.find(
            '{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}fileinfo/' +
            '{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}filepath')
        filePath.text = self.location_string
        return self.record

    def get_location_string(self):
        return self._location_string

    def set_location_string(self, value):
        self._location_string = value

    def get_record(self):
        return self._record

    def set_record(self, value):
        if not isinstance(self, LDRItem):
            raise ValueError(
                "Can only modify a fits record that comes as an ldritem")
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
                self._subject = ElementTree.parse(tempfile)

    record = property(get_record, set_record)
    location_string = property(get_location_string, set_location_string)
