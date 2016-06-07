from abc import abstractmethod, ABCMeta

from .abc.packager import Packager
from ...structures.segment import Segment


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class SegmentPackager(Packager, metaclass=ABCMeta):
    """
    The base class for all segment packagers

    defines the msuite packager they should use to package their contents, as
    well as the interface for setting the segment id
    """

    _msuite_packager = None
    _id_prefix = None
    _id_num = None

    @abstractmethod
    def __init__(self):
        super().__init__()

    def set_msuite_packager(self, value):
        self._msuite_packager = value

    def get_msuite_packager(self):
        return self._msuite_packager

    def set_id_prefix(self, value):
        self._id_prefix = value

    def get_id_prefix(self):
        return self._id_prefix

    def set_id_num(self, value):
        self._id_num = value

    def get_id_num(self):
        return self._id_num

    msuite_packager = property(get_msuite_packager, set_msuite_packager)
    id_prefix = property(get_id_prefix, set_id_prefix)
    id_num = property(get_id_num, set_id_num)
