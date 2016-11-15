from abc import ABCMeta, abstractmethod


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class LDRItem(metaclass=ABCMeta):
    """
    Specifies methods which must be implemented in order for a subclass
    to qualify as a representation of an LDR Item in the UChicago
    Library Digital Repository Specification

    Provides generalizable functionality to facilitate "with" syntax when
    properly implemented.
    """
    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def write(self):
        pass

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def exists(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __repr__(self):
        return self.get_name()

    def get_name(self):
        return self._item_name

    def set_name(self, value):
        if isinstance(value, str):
            self._item_name = value
        else:
            raise ValueError("item_name must be a string")

    def get_is_flo(self):
        return self.is_flo

    def set_is_flo(self, value):
        if isinstance(value, bool):
            self._is_flo = value
        else:
            raise ValueError("is_flo must be either True or False")

    def get_size(self, buffering=1024*1000*100):
        if self.exists():
            size = 0
            with self.open() as f:
                data = f.read(buffering)
                while data:
                    size = size + len(data)
                    data = f.read(buffering)
            return size
        else:
            return 0

    # TODO: Potentially phase out item_name?
    item_name = property(get_name, set_name)
    is_flo = property(get_is_flo, set_is_flo)
