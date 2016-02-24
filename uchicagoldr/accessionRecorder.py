from csv import DictReader
from re import match, finditer
from hierarchicalrecord import HierarchicalRecord


class AccessionRecorder(object):
    def __init__(self, record=None, conf=None):
        self.set_record(record)
        self.set_conf(conf)

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
            raise AttributeError("There is no record associated with this instance!")
        if self.get_conf() is None:
            raise AttributeError("This is no conf associated with this instance!")
        for x in self.get_conf().get_data():
            field_name = x['Field Name']
            value_type = x['Value Type']
            obligation = x['Obligation']
            cardinality = x['Cardinality']
            validation = x['Validation']
            applicable_values = self._gather_applicable_values(field_name)
            if obligation == 'r':
                if len(nodes_applicable) == 0:
                    return (False, "A required node is not present")
            if cardinality != 'n':
                if len(nodes_applicable) != int(cardinality):
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
                for node in nodes_applicable:
                    for field in node:
                        if not isinstance(node[field], type_comp):
                            return (False, "A node contains an illegal data type.")
            if validation:
                for node in nodes_applicable:
                    for field in node:
                        if not match(validation, str(node[field])):
                            return (False, "A node does not validate against its regex.")
            return (True, None)

    def _gather_applicable_values(self, field_name):
        result = []
        for x in record.keys():
            comp = x[:-1]
            dot_count = len([x for x in comp if x == "."])
            dot_indices = [m.start() for m in finditer('\.', x)]
            comp = "".join([y for i,y in enumerate(comp) if i not in dot_indices])




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
