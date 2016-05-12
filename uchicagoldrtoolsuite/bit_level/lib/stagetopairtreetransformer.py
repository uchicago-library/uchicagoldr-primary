
from .archive import Archive
from .ldritemoperations import get_archivable_identifier
from .abc.transformer import Transformer


class StageToPairTreeTransformer(Transformer):
    def __init__(self, origin_structure):
        self.origin_structure = origin_structure
        self.destination_structure = Archive()

        def get_origin_structure(self):
            return self._origin_structure

        def set_origin_structure(self, value):
            if isinstance(value, Stage):
                self._origin_structure = value
            else:
                raise ValueError("StageToPairtreeTransformer must have an " +
                                 "of a Stage in origin_structure")

        def get_destination_structure(self):
            return self._destination_structure

        def set_destination_structure(self, value):
            if isinstance(value, Archive):
                self._destination_structure = value
            else:
                raise ValueError("StageToPairtreeTransformer must have an " +
                                 "of an Archive in destination_structure")
