from csv import DictReader
from re import match, search
from json import dumps


class AccessionRecorder(object):
    def __init__(self, record=None, conf=None):
        self.set_record(record)
        self.set_conf(conf)

    def set_record(self, record):
        if record is None:
            self.record = None
        if not isinstance(record, AccessionRecord):
            raise ValueError
        self.record = record

    def get_record(self):
        return self.record

    def set_conf(self, conf):
        if conf is None:
            self.conf = None
        if not isinstance(conf, AccessionRecordConfig):
            raise ValueError
        self.conf = conf

    def get_conf(self):
        return self.conf


class AccessionRecordConfig(object):
    def __init__(self, filepath):
        self.set_filepath(filepath)
        self.set_data(self.read_file())

    def read_file(self):
        with open(self.filepath, 'r') as f:
            reader = DictReader(f)
            rows = []
            for row in reader:
                rows.append(row)
            return rows

    def set_filepath(self, filepath):
        self.filepath = filepath

    def get_filepath(self):
        return self.filepath

    def set_data(self, conf):
        self.conf = conf

    def get_data(self):
        return self.conf
