from uuid import uuid1


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class Family(object):

    _record_identifier = None
    _family_type = None
    _identifier = None
    _name = None
    _child_families = []
    _child_content_pointers = []

    def __init__(self, family_type, identifier=None, name=None,
                 child_families=[], child_content_pointers=[],
                 record_identifier=None):
        self.family_type = family_type
        if identifier is None:
            self.identifier = uuid1().hex
        else:
            self.identifier = identifier
        if child_families != []:
            self.child_families = child_families
        if child_content_pointers != []:
            self.child_content_pointers = child_content_pointers
        if record_identifier is not None:
            self.record_identifier = record_identifier
        if name is not None:
            self.name = name

    def __repr__(self):
        return str(self.dictify())

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
            index = len(self.get_child_families())
        self._child_families.insert(index, child_uuid)

    def get_child_family(self, index):
        return self.get_child_families()[index]

    def remove_child_family(self, index):
        del self.get_child_families[index]

    def add_child_content_pointer(self, child_uuid, index=None):
        if not isinstance(child_uuid, str):
            raise ValueError('Child uuids must be a string')
        if index is None:
            index = len(self.get_child_content_pointers())
        self._child_content_pointers.insert(index, child_uuid)

    def get_child_content_pointer(self, index):
        return self.get_child_content_pointers[index]

    def remove_child_content_pointer(self, index):
        del self.get_child_content_pointers[index]

    def set_record_identifier(self, record_identifier):
        if not isinstance(record_identifier, str):
            raise ValueError("record_identifier must be a string.")
        self._record_identifier = record_identifier

    def get_record_identifier(self):
        return self._record_identifier

    def del_record_identifier(self):
        self._record_identifier = None

    def del_record(self):
        self._record_identifier = None

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

    def dictify(self):
        r = {}
        r['identifier'] = self.identifier
        r['child_families'] = self.child_families
        r['child_content_pointers'] = self.child_content_pointers
        r['record_identifier'] = self.record_identifier
        r['family_type'] = self.family_type
        r['name'] = self.name
        return r

    family_type = property(get_family_type,
                           set_family_type)

    identifier = property(get_identifier,
                          set_identifier,
                          del_identifier)

    child_families = property(get_child_families,
                              set_child_families,
                              del_child_families)

    child_content_pointers = property(get_child_content_pointers,
                                      set_child_content_pointers,
                                      del_child_content_pointers)

    children = property(get_children,
                        set_children,
                        del_children)

    record_identifier = property(get_record_identifier,
                                 set_record_identifier,
                                 del_record_identifier)

    name = property(get_name,
                    set_name,
                    del_name)
