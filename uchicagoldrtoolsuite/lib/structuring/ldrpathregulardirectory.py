from os.path import relpath
from pathlib import Path
from .abc.ldritem import LDRDirectory

class LDRPathRegularDirectory(LDRDirectory):

    def __init__(self, param1):
        self.item_name = param1
        self.path = Path(self.item_name)
        self.is_flo = False
    
    def exists(self):
        return self.path.exists

    def getHierarchyInformation(self, root_to_cut):
        output = relpath(self.item_name, root_to_cut):
        if output.startswith(".."):
            raise ValueError("bad root_to_cut string passed")
        else:
            return output
        
    def is_flo(self):
        return False

    def set_is_flo(self, value):
        self._is_flo = False

    def get_is_flo(self):
        return sel._is_flo

    def get_path(self):
        return self._path

    def set_path(self, value):
        self._path = Path(value)

    def get_item_name(self):
        return self._item_name

    def set_item_name(self, value):
        return self._item_name
    
    path = property(get_path, set_path)
    is_flo = property(get_is_flo, set_is_flo)
    item_name = property(get_item_name, set_item_name)
