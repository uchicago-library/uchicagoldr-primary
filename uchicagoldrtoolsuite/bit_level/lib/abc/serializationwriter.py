from abc import ABCMeta, abstractmethod


__author__ = "Tyler Danstrom"
__email__ = "tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class SerializationWriter(metaclass=ABCMeta):
    """
    ABC for all Serialization Writers

    assures the .write() method
    """
    @abstractmethod
    def write(self):
        pass
