from csv import DictReader
from re import match
from copy import copy


class AccessionRecorder(object):
    def __init__(self, record=None):
        self.record = record

    def set_record(self, record):
        if not isinstance(record, AccessionRecord):
            raise ValueError
        self.record = record

    def get_record(self):
        return self.record


class AccessionRecord(object):
    def __init__(self, seed_dict=None, conf=None):
        if seed_dict:
            self.set_record(seed_dict)
        else:
            self.set_record({})

        self.conf = conf

    def _dotted_to_list(self, dotted_string):
        return dotted_string.split(".")

    def _list_to_dotted(self, in_list):
        for x in in_list:
            if "." in x:
                raise ValueError("'.' is a protected character in " +
                                 "record configuration key names.")
        return ".".join(in_list)

    def _get_value_from_key_list(self, keyList, start=None, index=None):
        if start is None:
            start = self.get_record()
        nextKey = keyList[0]
        if len(keyList) == 1:
            if index is None:
                return start[nextKey]
            else:
                return start[nextKey][index]
        else:
            assert(nextKey in start)
            return self._get_value_from_key_list(keyList[1:],
                                                start=start[nextKey],
                                                index=index)

    def _set_value_from_key_list(self, keyList, new_value, start=None, index=None):
        if start is None:
            start = self.get_record()
        nextKey = keyList[0]
        if len(keyList) == 1:
            if index is None:
                start[nextKey] = new_value
                return True
            else:
                start[nextKey][index] = new_value
        else:
            if nextKey not in start:
                start[nextKey] = {}
            self._set_value_from_key_list(keyList[1:], new_value,
                                         start=start[nextKey],
                                         index=index)

    def set_record(self, record):
        if not isinstance(record, dict):
            raise ValueError
        self.record = record

    def get_record(self):
        return self.record

    def set_conf(self, conf):
        self.conf = conf

    def get_conf(self):
        return self.conf

    def set_field(self, key, value, index=None):
        if isinstance(key, str):
            key = self._dotted_to_list(key)
        if not isinstance(key, list):
            raise ValueError()
        self._set_value_from_key_list(key, value, index=index)

    def get_field(self, key, index=None):
        if isinstance(key, str):
            key = self._dotted_to_list(key)
        if not isinstance(key, list):
            raise ValueError()
        return self._get_value_from_key_list(key, index=index)

    def add_to_field(self, key, value):
        if isinstance(key, str):
            key = self._dotted_to_list(key)
        if not isinstance(key, list):
            raise ValueError()
        self.get_field(key).append(value)

    def validate_against_conf(self):
        if self.conf is None:
            return True
        else:
            # logic for reading config and checking things
            return True
        return False

class AccessionRecordConfig(object):
    def __init__(self, filepath):
        self.set_filepath(filepath)
        self.set_conf(self.read_file())

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

    def set_conf(self, conf):
        self.conf = conf

    def get_conf(self):
        return self.conf
