from uuid import uuid1

from hierarchicalrecord.hierarchicalrecord import HierarchicalRecord

__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class Family(object):

    _record = None
    _family_type = None
    _identifier = None
    _name = None
    _child_families = []
    _child_content_pointers = []

    def __init__(self, family_type, identifier=None, name=None,
                 children=[], record=None):
        self.set_family_type(family_type)
        if identifier is None:
            self._identifier = str(uuid1())
        else:
            self.set_identifier(identifier)
        if children != []:
            self.set_children(children)
        if record is not None:
            self.set_record(record)
        if name is not None:
            self.set_name(name)

    def get_identifier(self):
        return self._identifier

    def set_identifier(self, identifier):
        if not isinstance(identifier, str):
            raise ValueError('Identifiers must be strings')
        self._identifier = identifier

    def del_identifier(self):
        self._identifier = None

    def get_children(self):
        return self.get_child_content_pointers + self.get_child_families

    def set_children(self, children):
        raise NotImplemented()

    def del_children(self):
        while self.get_child_family(0):
            self._child_families.pop()
        while self.get_child_content_pointer(0):
            self._child_content_pointers.pop()

    def get_child_families(self):
        return self._child_families

    def set_child_families(self, child_families):
        self.del_child_families()
        for x in child_families:
            self.add_child_family(x)

    def del_child_families(self):
        self._child_families = []

    def get_child_content_pointers(self):
        return self._child_content_pointers

    def set_child_content_pointers(self, child_content_pointers):
        self.del_child_content_pointers()
        for x in child_content_pointers:
            self.add_child_content_pointer(x)

    def del_child_content_pointers(self):
        self._child_content_pointers = []

    def add_child_family(self, child_uuid, index=None):
        if not isinstance(child_uuid, str):
            raise ValueError('Child uuids must be a string')
        if index is None:
            index = len(self.get_child_families)
        self._child_families.insert(index, child_uuid)

    def get_child_family(self, index):
        return self.get_child_families()[index]

    def remove_child_family(self, index):
        del self.get_child_families[index]

    def add_child_content_pointer(self, child_uuid, index=None):
        if not isinstance(child_uuid, str):
            raise ValueError('Child uuids must be a string')
        if index is None:
            index = len(self.get_child_content_pointers)
        self._child_families.insert(index, child_uuid)

    def get_child_content_pointer(self, index):
        return self.get_child_content_pointers[index]

    def remove_child_content_pointer(self, index):
        del self.get_child_content_pointers[index]

    def set_record(self, record):
        if not isinstance(record, HierarchicalRecord):
            raise ValueError('Records associated with families must be ' +
                             'HierarchicalRecord instances')
        self._record = record

    def get_record(self):
        return self._record

    def del_record(self):
        self._record = None

    def set_family_type(self, family_type):
        if not isinstance(family_type, str):
            raise ValueError('Family type should be a str')
        self._family_type = family_type

    def get_family_type(self):
        return self._family_type

    def get_name(self):
        return self._name

    def set_name(self, name):
        if not isinstance(name, str):
            raise ValueError('Names must be strs')
        self._name = name

    def del_name(self):
        self._name = None

    property(get_identifier, set_identifier, del_identifier)
    property(get_child_families, set_child_families, del_child_families)
    property(get_child_content_pointers, set_child_content_pointers, del_child_content_pointers)
    property(get_record, set_record, del_record)
    property(get_family_type, set_family_type)
    property(get_name, set_name, del_name)
