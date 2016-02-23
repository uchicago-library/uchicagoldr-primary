from csv import DictReader
from re import match, search


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


class AccessionRecord(object):
    def __init__(self):
        self.record = {}

    def _dotted_to_list(self, dotted_string):
        return dotted_string.split(".")

    def _list_to_dotted(self, in_list):
        for x in in_list:
            if "." in x:
                raise ValueError("'.' is a protected character in " +
                                 "record configuration key names.")
        return ".".join(in_list)

#    def _get_value_from_key_list(self, keyList, start=None, index=None):
#        if start is None:
#            start = self.get_record()
#        nextKey = keyList[0]
#        if len(keyList) == 1:
#            if index is None:
#               return start[nextKey]
#            else:
#                return start[nextKey][index]
#        else:
#           if nextKey not in start:
#               raise KeyError
#            return self._get_value_from_key_list(keyList[1:],
#                                                 start=start[nextKey],
#                                                 index=index)

    def _split_path_strings(self, in_str):
        new_key_index = None
        new_key_index_str = search(r'\d+$', in_str)
        if new_key_index_str:
            new_key_index = new_key_index_str.group()
        if new_key_index:
            new_key_str = in_str.rstrip(new_key_index)
            new_key_index = int(new_key_index)
        else:
            new_key_str = in_str
            new_key_index = 0
        return new_key_str, new_key_index

    def _get_value_from_key_list(self, keyList, start=None):
        if start is None:
            start = self.get_record()
        new_key_str, new_key_index = self._split_path_strings(keyList[0])
        if len(keyList) == 1:
            return start[new_key_str][new_key_index]
        else:
            return self._get_value_from_key_list(keyList[1:],
                                                 start=start[new_key_str][new_key_index])

    def _set_field_from_key_list(self, keyList, new_value, start=None):
        if start is None:
            start = self.get_record()
        new_key_str, new_key_index = self._split_path_strings(keyList[0])
        if len(keyList) == 1:
            start[keyList[0]] = new_value
        else:
            start[new_key_str][new_key_index] = {}
            self._set_field_from_key_list(keyList[1:], new_value,
                                          start=start[new_key_str][new_key_index])

    def _edit_field_from_key_list(self, keyList, new_value, start=None):
        if start is None:
            start = self.get_record()
        new_key_str, new_key_index = self._split_path_strings(keyList[0])
        if len(keyList) == 1:
            start[new_key_str][new_key_index] = new_value
        else:
            self._edit_field_from_key_list(keyList[1:], new_value,
                                           start=start[new_key_str][new_key_index])

    def _init_field_from_key_list(self, keyList, start=None):
        if start is None:
            start = self.get_record()
        new_key_str, new_key_index = self._split_path_strings(keyList[0])
        if new_key_str not in start:
            start[new_key_str] = [""]
        while len(start[new_key_str]) < new_key_index+1:
            start[new_key_str].append("")
        if len(keyList) > 1:
            if start[new_key_str][new_key_index] == "":
                start[new_key_str][new_key_index] = {}
            self._init_field_from_key_list(keyList[1:],
                                           start=start[new_key_str][new_key_index])

    def _add_to_field_from_key_list(self, keyList, new_value, start=None):
        if start is None:
            start = self.get_record()
        new_key_str, new_key_index = self._split_path_strings(keyList[0])
        if len(keyList) == 1:
            start[new_key_str].append(new_value)
        else:
            self._add_to_field_from_key_list(keyList[1:], new_value,
                                             start=start[new_key_str][new_key_index])

    def _check_if_field_exists(self, keyList, start=None):
        if start is None:
            start = self.get_record()
        new_key_str, new_key_index = self._split_path_strings(keyList[0])
        if new_key_str not in start:
            return False
        if new_key_index > len(start[new_key_str])-1:
            return False
        if len(keyList) == 1:
            return True
        else:
            return self._check_if_field_exists(keyList[1:],
                                               start=start[new_key_str][new_key_index])

    def set_record(self, record):
        if not isinstance(record, dict):
            raise ValueError
        self.record = record

    def get_record(self):
        return self.record

    def set_field(self, key, value):
        if isinstance(key, str):
            key = self._dotted_to_list(key)
        if not isinstance(key, list):
            raise ValueError()
        if self._check_if_field_exists(key):
            self._edit_field_from_key_list(key, value)
        else:
            self._init_field_from_key_list(key)
            self._edit_field_from_key_list(key, value)


    def get_field(self, key):
        if isinstance(key, str):
            key = self._dotted_to_list(key)
        if not isinstance(key, list):
            raise ValueError()
        return self._get_value_from_key_list(key)

    def add_to_field(self, key, value):
        if isinstance(key, str):
            key = self._dotted_to_list(key)
        if not isinstance(key, list):
            raise ValueError()
        if self._check_if_field_exists(key):
            self._add_to_field_from_key_list(key, value)
        else:
            raise ValueError('field does not exist')


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
