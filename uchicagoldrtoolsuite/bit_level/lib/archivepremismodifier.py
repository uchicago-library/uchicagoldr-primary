
from tempfile import TemporaryFile

from pypremis.lib import PremisRecord

from .archivepremisevent import ArchivePremisEvent


class ArchivePremisModifier(object):
    def __init__(self, record, location_string):
        self.record = record
        self.new_location = location_string
        self.archive_event = ArchivePremisEvent

    def change_record(self):
        objid_types = []
        objid_values = []
        for obj in self.record.get_object_list():
            for storage in obj.get_storage():
                content_loc = storage.get_contentLocation()
                content_loc.set_contentLocationValue(self.new_location)
            for characteristic in obj.get_objectCharacteristics():
                objid = characteristic.get_objectIdentifier()
                objid_types.append(objid.get_objectIdentifierType())
                objid_values.append(objid.get_objectIdentifierValue())
        objids = zip(objid_types, objid_values)
        new_event = self.archive_event(objids)
        self.record.event_list.append(new_event)

    def modify_record(self):
        new_event = self.archive_event.build_event()
        self.record.event_list.append(new_event)
        self.enter_new_contentLocation()

    def get_record(self):
        return self._record

    def set_record(self, value):
        with TemporaryFile() as tempfile:
            with value.open('rb') as read_file:
                while True:
                    buf = read_file.read(1024)
                    if buf:
                        tempfile.write(buf)
                    else:
                        break
                tempfile.seek(0)
                self._subject = PremisRecord(frompath=tempfile)


    def get_location(self):
        return self._new_location

    def set_location(self, value):
        self._new_location = value

    record = property(get_record, set_record)
    new_location = property(get_location, set_location)
