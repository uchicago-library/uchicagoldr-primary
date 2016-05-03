from abc import abstractproperty

from .abc.serializationreader import SerializationReader


class StagingSerializationReader(SerializationReader):
    def __init__(self):
        pass

    def get_stage_id(self):
        return self._stage_id

    def set_stage_id(self, value):
        self._stage_id = value

    stage_id = abstractproperty(get_stage_id, set_stage_id)
