from csv import DictReader
from re import match, subn
from hierarchicalrecord import HierarchicalRecord


class AccessionRecorder(object):
    def __init__(self, record=None, conf=None):
        if record:
            self.set_record(record)
        else:
            self.record = None
        if conf:
            self.set_conf(conf)
        else:
            self.conf = None

    def _generalize_keys(self, key):
        result = subn("\d*$", "", key)[0]
        result = subn("\d*\.", ".", result)[0]
        return result

    def _gather_applicable_values(self, field_name):
        result = []
        for x in self.get_record().keys():
            comp = self._generalize_keys(x)
            if comp == field_name:
                result.append(self.get_record()[x])
        return result

    def set_record(self, record):
        if record is None:
            self.record = None
        if not isinstance(record, HierarchicalRecord):
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

    def validate_record(self, strict=True):
        if self.get_record() is None:
            raise AttributeError("There is no record associated " +
                                 "with this instance!")
        if self.get_conf() is None:
            raise AttributeError("This is no conf associated " +
                                 "with this instance!")
        for x in self.get_conf().get_data():
            field_name = x['Field Name']
            value_type = x['Value Type']
            obligation = x['Obligation']
            cardinality = x['Cardinality']
            validation = x['Validation']
            nested = False
            if "." in field_name:
                nested = True
            applicable_values = self._gather_applicable_values(field_name)
            if obligation == 'r':
                if nested is False:
                    if len(applicable_values) == 0:
                        return (False, "A required node is not present\n" +
                                "Node: {}".format(field_name))
                else:
                    parent_key = ".".join(field_name.split(".")[:-1])
                    leaf_key = field_name.split(".")[-1]
                    for y in self._gather_applicable_values(parent_key):
                        if leaf_key not in y:
                            return (False, "A required node is not present.")
            if len(applicable_values) > 0:
                its_there = True
            else:
                its_there = False
            if its_there is False:
                continue
            if cardinality != 'n':
                if len(applicable_values) != int(cardinality):
                    return (False, "A nodes cardinality is incorrect.")
            if value_type:
                allowed_types = [('str', str),
                                 ('dict', dict),
                                 ('int', int),
                                 ('bool', bool),
                                 ('float', float)]
                for x in allowed_types:
                    if x[0] == value_type:
                        type_comp = x[1]
                for value in applicable_values:
                    if not isinstance(value, type_comp):
                        return (False, "A node contains an illegal data type.")
            if validation:
                for value in applicable_values:
                    if not match(validation, value):
                        wrong_key = None
                        for n in self.get_record().keys():
                            if self.get_record()[n] == value:
                                wrong_key = n
                        return (False, "A node does not validate " +
                                "against its regex.\n" +
                                "Node: {}\n".format(wrong_key) +
                                "Value: {}\n".format(value) +
                                "Pattern: {}".format(validation))
        return (True, None)


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
