from abc import ABCMeta, abstractmethod, abstractproperty

class LDRDirectory(metaclass=abc.ABCMeta):

    @abstractmethod
    def getHierarchyInformation(self):
        pass

    @abstractmethod
    def exists(self):
        pass
    
    def get_item_name(self):
        return self._item_name

    def set_item_name(self, value):
        self._item_name = value

    def get_path(self):
        return self._path

    def set_path(self, value):
        self._path = value

    def set_is_flo(self, value):
        self._path = False

    def get_is_flo(self, value):
        return self._path
    
    item_name = abstractproperty(get_item_name, set_item_name)
    path = abstractproperty(get_path, set_path)
    is_flo = abstractproperty(get_path, set_path)
