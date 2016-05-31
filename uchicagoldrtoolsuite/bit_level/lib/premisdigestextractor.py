
from collections import namedtuple
from tempfile import TemporaryFile

from pypremis.lib import PremisRecord

from .abc.ldritem import LDRItem


class PremisDigestExtractor(object):
    def __init__(self, record):
        self.record = record

    def extract_digests(self):
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
        return self._record

    def set_record(self, value):
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
