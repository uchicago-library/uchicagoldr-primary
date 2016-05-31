
import json
from tempfile import TemporaryFile

from hierarchicalrecord.hierarchicalrecord import HierarchicalRecord

from .abc.auditor import Auditor
from .abc.ldritem import LDRItem


class AccessionRecordModifier(object):
    def __init__(self, subject):
        self.record = record


    def get_subject(self):
        return self._subject

    def add_restriction_info(self, restriction_list):
        if self.record.get('Restrictions'):
            orig = set(self.record['Restrictions'])
            for n_restriction in restriction_list:
                orig.add(n_restriction)
            self.record['Restrictions'] = list(orig)
        else:
            self.record['Restrictions'] = restriction_list

    def write(self, file_location):
        jsonified_hrecord = json.loads(str(self.record))
        with open(file_location, 'wb') as writing_file:
            json.dump(bytes(jsonified_hrecord.encode('utf-8')))

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
                    hrecord.data_object = data
                    self._record = hrecord
        else:
            raise ValueError(
                "AccessionRecordAuditor can only take an ldritem as subject")


    record = property(get_subject, set_subject)
