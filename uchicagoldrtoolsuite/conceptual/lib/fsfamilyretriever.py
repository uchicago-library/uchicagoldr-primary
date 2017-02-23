from os.path import isabs
from os.path import join
from json import load

from .abc.familyretriever import FamilyRetriever

class FileSystemFamilyRetriever(FamilyRetriever):

    _base_dir = None

    def __init__(self, base_dir=None):
        if base_dir is not None:
            self.base_dir = base_dir
        if base_dir is None:
            raise ValueError("base_dir must be set, either in the class as " +
                             "a default for all spawned " +
                             "FileSystemFamilyRetrievers, or in the init.")

    def get_base_dir(self):
        return self._base_dir

    def set_base_dir(self, base_dir):
        if not isabs(base_dir):
            raise ValueError("base_dir must be an absolute path")
        self._base_dir = base_dir

    def del_base_dir(self):
        self._base_dir = None

    def retrieve(self, uuid):
        fp = join(self.base_dir, uuid)
        with open(fp, 'r') as f:
            j = load(f)
            return self.pack(j['family_type'],
                            j['identifier'],
                            j['name'],
                            j['child_families'],
                            j['child_content_pointers'],
                            j['record_identifier'])

    base_dir = property(get_base_dir, set_base_dir, del_base_dir)
