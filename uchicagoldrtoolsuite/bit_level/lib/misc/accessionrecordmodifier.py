
import json
from tempfile import TemporaryFile

from hierarchicalrecord.hierarchicalrecord import HierarchicalRecord

from ..auditors.abc.auditor import Auditor
from ..ldritems.abc.ldritem import LDRItem


class AccessionRecordModifier(object):
    def __init__(self, subject):
        self.record = subject

    def add_restriction_info(self, restriction_list):

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
        jsonified_hrecord = self.record.toJSON()
        with open(file_location, 'wb') as writing_file:
            writing_file.write(bytes(jsonified_hrecord.encode('utf-8')))

    def get_record(self):
        return self._record

    def set_record(self, value):
        if isinstance(value, LDRItem):
            with TemporaryFile() as tempfile:
                with value.open('rb') as read_file:
                    while True:
                        buf = read_file.read(1024)
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
                "AccessionRecordAuditor can only take an ldritem as subject")


    record = property(get_record, set_record)
