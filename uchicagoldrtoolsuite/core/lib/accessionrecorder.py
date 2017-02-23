from csv import DictReader
from re import match, subn

from hierarchicalrecord.hierarchicalrecord import HierarchicalRecord


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class AccessionRecorder(object):
    """
    AccessionRecorder is a class built to facilitate building and validating
    accession record files against a CSV format config.

    __Attributes__

    * record (HierarchicalRecord): the record instance to be worked with
    * conf (AccessionRecordConfig): the config to be used when applicable
    """
    def __init__(self, record=None, conf=None):
        """
        Initialize a new AccessionRecorder instance, potentially with
        associated record and config values

        __KWArgs__

        * record (HierarchicalRecord): a record instance to associate with
        * config (AccessionRecordConfig): a config instance to associate with
        """
        if record:
            self.set_record(record)
        else:
            self.record = None
        if conf:
            self.set_conf(conf)
        else:
            self.conf = None

    def _generalize_keys(self, key):
        """
        Generalize keys with indices, for comparison against general dotted
        syntax

        __Args__

        1. key (str): a str of a dotted key with indices

        __Returns__

        1. result (str): a str of a dotted key with no indices
        """
        result = subn("\d*$", "", key)[0]
        result = subn("\d*\.", ".", result)[0]
        return result

    def _gather_applicable_values(self, field_name):
        """
        Gather all values associated with a generalized key

        __Args__

        1. field_name (str): the generalized key/field name

        __Returns__

        1. result (list): a list of the values associated with all instances
        of the key
        """
        result = []
        for x in self.get_record().keys():
            comp = self._generalize_keys(x)
            if comp == field_name:
                result.append(self.get_record()[x])
        return result

    def _gather_applicable_keys(self, field_name):
        """
        Gather all keys associated with a generalized key

        __Args__

        1. field_name (str): the generalized key/field name

        __Returns__

        1. result (list): a list of the specific keys associated with the
        generalized key
        """
        result = []
        for x in self.get_record().keys():
            comp = self._generalize_keys(x)
            if comp == field_name:
                result.append(x)
        return result


    def _gather_applicable_fields(self, field_name):
        """
        Gather all fields associated with a generalized key

        __Args__

        1. field_name (str): the generalized key

        __Returns__

        1. result (list): a list of fields (lists themselves)
        """
        result = []
        for x in self.get_record().keys():
            comp = self._generalize_keys(x)
            if comp == field_name:
                key = subn("\d*$", "", x)[0]
                result.append(self.get_record()[key])
        return result

    def set_record(self, record):
        """
        set the record instance associated with this instance

        __Args__

        1. record (HierarchicalRecord or None): A HierarchicalRecord instance to
        associate with this recorder instance. None to clear it.
        """
        if record is None:
            self.record = None
            return
        if not isinstance(record, HierarchicalRecord):
            raise ValueError
        self.record = record

    def get_record(self):
        """
        return the record instance associated with this recorder instance

        __Returns__
        1. (HierarchicalRecord): the record instance
        """
        return self.record

    def set_conf(self, conf):
        """
        set the AccessionRecordConfig instance associated with this instance

        __Args__

        1. conf (AccessionRecordConfig): the instance to be associated with
        this recorder instance
        """
        if conf is None:
            self.conf = None
            return
        if not isinstance(conf, AccessionRecordConfig):
            raise ValueError
        self.conf = conf

    def get_conf(self):
        """
        return the config instance associated with this recorder instance

        __Returns__

        1. (AccessionRecordConfig): the associated config instance
        """
        return self.conf

    def validate_record(self, strict=True):
        """
        validate a record against a config

        __KWArgs__

        * stict: if undocumented fields are in the record fail validation

        __Returns__

        (tuple): a two element tuple containing a bool denoting validation
        status and potentitally an explanation string
        """
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
            required_children = x['Children Required']
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
            if required_children:
                for x in self._gather_applicable_fields(field_name):
                    if len(x) < int(required_children):
                        return (False, "A node does not meet the minimum " +
                                "requirements for # of children\n" +
                                "Node: {}\n".format(field_name) +
                                "Children Detected: {}\n".format(str(len(x))) +
                                "Required Children: {}".format(required_children))
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
        """
        generate the shortest/least verbose valid record structure
        from the associated conf
        """
        self.generate_record(sparse=True)

    def generate_full_record(self):
        """
        Generate a valid record from the associated conf which includes
        every field and additionally duplicates every field with cardinality "n"
        """
        self.generate_record()

    def generate_record(self, sparse=False):
        """
        generate a new record given a config

        __KWArgs__

        * sparse (bool): If true generate a minimal record which omits optional
            fields and never duplicates fields if it doesn't have to. If true
            generate a record with every field, that duplicates every
            duplicatable field.
        """
        if self.get_record() is not None:
            raise AttributeError("There is already a record associated " +
                                 "with this instance!")
        if self.get_conf() is None:
            raise AttributeError("This is no conf associated " +
                                 "with this instance!")
        self.set_record(HierarchicalRecord())
        for x in self.get_conf().get_data():
            obligation = x['Obligation']
            if obligation != "r" and sparse:
                continue
            field_name = x['Field Name']
            value_type = x['Value Type']
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
                if sparse:
                    cardinality = '1'
                else:
                    cardinality = '2'

            if not nested:
                for y in range(int(cardinality)):
                    self.get_record()[field_name+str(y)] = dummy_value
            else:
                parent_key = ".".join(field_name.split(".")[:-1])
                leaf_key = field_name.split(".")[-1]
                for y in self._gather_applicable_keys(parent_key):
                    for z in range(int(cardinality)):
                        self.get_record()[y+"."+leaf_key+str(z)] = dummy_value



    def populate_from_csv(self, filepath):
        """
        read a csv of key value pairs, populating or altering a record instance

        __Args__

        * filepath (str): the path to a csv file.
        """
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
    """
    wraps a csv formatted accession record config, easily exposing the data

    __Attributes__

    * filepath (str): the file path for a config csv
    * data (list): the config data by row
    """
    def __init__(self, filepath):
        """
        initialize an AccessionRecordConfig instance.

        __Args__

        1. filepath (str): a path to a config csv
        """
        self.set_filepath(filepath)
        self.set_data(self.read_file())

    def read_file(self):
        """
        read the associated file path into a list of dictionaries

        __Returns__

        1. rows (list): the list of dictionaries
        """
        with open(self.filepath, 'r') as f:
            reader = DictReader(f)
            rows = []
            for row in reader:
                rows.append(row)
            return rows

    def set_filepath(self, filepath):
        """
        sets the filepath to the associated csv file

        __Args__

        1. filepath (str): the filepath to a config csv
        """
        self.filepath = filepath

    def get_filepath(self):
        """
        returns the filepath associated with the instance

        __Returns__

        1. (str): the filepath associated with the instance
        """
        return self.filepath

    def set_data(self, conf):
        """
        set the data associated with a config instance

        __Args__

        1. conf (list): a list of dictionaries to be used as the data of the
        instance
        """
        self.conf = conf

    def get_data(self):
        """
        return the list of config rows

        __Returns__

        1. (list): a list of dictionaries containing config information
        """
        return self.conf
