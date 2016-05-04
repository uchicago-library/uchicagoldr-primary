from abc import abstractproperty

from .abc.serializationreader import SerializationReader


__author__ = "Tyler Danstrom"
__email__ = "tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class StagingSerializationReader(SerializationReader):
    def __init__(self):
        pass

    def get_stage_id(self):
        return self._stage_id

    def set_stage_id(self, value):
        self._stage_id = value

    stage_id = abstractproperty(get_stage_id, set_stage_id)
