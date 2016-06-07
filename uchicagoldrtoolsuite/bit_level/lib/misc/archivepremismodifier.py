
from tempfile import TemporaryFile

from pypremis.lib import PremisRecord

from .archivepremisevent import ArchivePremisEvent

__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class ArchivePremisModifier(object):
    """The ArchivePremisModifier object is meant to modify a premis record
    with the data necessary for it to be valid records in the permanent archive 
    space
    """
    def __init__(self, record, location_string):
        """initializes an ArchivePremisModifier object
        
        __Args__
        1. record (LDRItem): a file-like objet pointing to a PREMIS record
        2. location_string (str): a file path string representing a path to write 
        the updated PREMIS record 
        """
        self.record = record
        self.new_location = location_string
        self.archive_event = ArchivePremisEvent

    def change_record(self):
        """this function updates the record data attribute with a new content_loc
        and creates a PREMIS archive event and adds the new event to the record
        event list
        """
        objid_types = []
        objid_values = []
        for obj in self.record.get_object_list():
            for storage in obj.get_storage():
                content_loc = storage.get_contentLocation()
                content_loc.set_contentLocationValue(self.new_location)
            objids = obj.get_objectIdentifier()
            for objid in objids:
                objid_types.append(objid.get_objectIdentifierType())
                objid_values.append(objid.get_objectIdentifierValue())
                objids = zip(objid_types, objid_values)
        new_event = self.archive_event(objids).build_event()
        self.record.events_list.append(new_event)

    def get_record(self):
        """returns the record data attribute
        """
        return self._record

    def set_record(self, value):
        """sets the record data attribute
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
                self._record = PremisRecord(frompath=tempfile)


    def get_location(self):
        """returns the new_location data attribute value
        """
        return self._new_location

    def set_location(self, value):
        """sets the new_location data attribute value
        """
        self._new_location = value

    record = property(get_record, set_record)
    new_location = property(get_location, set_location)
