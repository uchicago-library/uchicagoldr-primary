from csv import DictReader
from re import match, subn
from uchicagoldr.hierarchicalrecord import HierarchicalRecord


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
            return
        if not isinstance(record, HierarchicalRecord):
            raise ValueError
        self.record = record

    def get_record(self):
        return self.record

    def set_conf(self, conf):
        if conf is None:
            self.conf = None
            return
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
        if strict is True:
            field_names = [x['Field Name'] for x in self.get_conf().get_data()]
            for key in self.get_record().keys():
                if self._generalize_keys(key) not in field_names:
                    return (False, "A key which appears in the record " +
                            "does not appear in the validation config.\n" +
                            "Key: {}".format(key))
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
                            return (False, "A required node is not present\n" +
                                    "Node: {}".format(field_name))
            if len(applicable_values) > 0:
                its_there = True
            else:
                its_there = False
            if its_there is False:
                continue
            if cardinality != 'n':
                if len(applicable_values) != int(cardinality):
                    return (False, "A nodes cardinality is incorrect.\n" +
                            "Node: {}\n".format(field_name) +
                            "Observed Cardinality: {}\n".format(str(len(applicable_values))) +
                            "Specificed Cardinality: {}".format(cardinality))
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
                        return (False, "A node contains an illegal data type.\n" +
                                "Node: {}\n".format(field_name) +
                                "Observed Data Type: {}\n".format(str(type(value))) +
                                "Specified Data Type: {}".format(value_type))
            if validation:
                for value in applicable_values:
                    if not match(validation, str(value)):
                        return (False, "A node does not validate " +
                                "against its regex.\n" +
                                "Node: {}\n".format(field_name) +
                                "Value: {}\n".format(value) +
                                "Pattern: {}".format(validation))
        return (True, None)

    def generate_minimal_record(self):
        if self.get_record() is not None:
            raise AttributeError("There is already a record associated " +
                                 "with this instance!")
        if self.get_conf() is None:
            raise AttributeError("This is no conf associated " +
                                 "with this instance!")
        self.set_record(HierarchicalRecord())
        for x in self.get_conf().get_data():
            field_name = x['Field Name']
            value_type = x['Value Type']
            obligation = x['Obligation']
            cardinality = x['Cardinality']
            nested = False
            if "." in field_name:
                nested = True
            allowed_types = [('str', 'default_string'),
                             ('dict', {}),
                             ('int', 0),
                             ('bool', False),
                             ('float', float(0))]
            dummy_value = None
            for x in allowed_types:
                if value_type == x[0]:
                    dummy_value = x[1]

            if obligation != "r":
                continue

            if cardinality != "n":
                if not nested:
                    for y in range(int(cardinality)):
                        self.get_record()[field_name+str(y)] = dummy_value
                else:
                    parent_key = ".".join(field_name.split(".")[:-1])
                    leaf_key = field_name.split(".")[-1]
                    num_parents = len(
                        self._gather_applicable_values(parent_key))
                    for y in range(num_parents):
                        for z in range(int(cardinality)):
                            self.get_record()[parent_key+str(y) + "." +
                                              leaf_key+str(z)] = dummy_value
            else:
                if not nested:
                    self.get_record()[field_name+"0"] = dummy_value
                else:
                    parent_key = ".".join(field_name.split(".")[:-1])
                    leaf_key = field_name.split(".")[-1]
                    num_parents = len(
                        self._gather_applicable_values(parent_key))
                    for y in range(num_parents):
                            self.get_record()[parent_key+str(y) + "." +
                                              leaf_key+"0"] = dummy_value

    def generate_full_record(self):
        if self.get_record() is not None:
            raise AttributeError("There is already a record associated " +
                                 "with this instance!")
        if self.get_conf() is None:
            raise AttributeError("This is no conf associated " +
                                 "with this instance!")
        self.set_record(HierarchicalRecord())
        for x in self.get_conf().get_data():
            field_name = x['Field Name']
            value_type = x['Value Type']
            obligation = x['Obligation']
            cardinality = x['Cardinality']
            nested = False
            if "." in field_name:
                nested = True
            allowed_types = [('str', 'default_string'),
                                ('dict', {}),
                                ('int', 0),
                                ('bool', False),
                                ('float', float(0))]
            dummy_value = None
            for x in allowed_types:
                if value_type == x[0]:
                    dummy_value = x[1]

            if cardinality == 'n':
                cardinality = '2'

            if not nested:
                for y in range(int(cardinality)):
                    self.get_record()[field_name+str(y)] = dummy_value
            else:
                parent_key = ".".join(field_name.split(".")[:-1])
                leaf_key = field_name.split(".")[-1]
                num_parents = len(self._gather_applicable_values(parent_key))
                for y in range(num_parents):
                    for z in range(int(cardinality)):
                        self.get_record()[parent_key+str(y)+"."+leaf_key+str(z)] = dummy_value

    def populate_from_csv(self, filepath):
        with open(filepath, 'r') as f:
            reader = DictReader(f)
            for row in reader:
                value = row['value']
                if value == "True":
                    value = True
                if value == "False":
                    value = False
                self.get_record()[row['key']] = value


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
