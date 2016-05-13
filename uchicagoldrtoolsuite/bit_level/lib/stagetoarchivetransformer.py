
from .archive import Archive
from .abc.transformer import Transformer
from .stage import Stage


class StageToArchiveTransformer(Transformer):
    def __init__(self, origin_structure):
        self.origin_structure = origin_structure
        self.destination_structure = None

    def transform(self, defined_id=None, make_noid=False):
        print(self.destination_structure)
        if self.destination_structure is not None:
            raise TypeError("a transformation already occured.")
        self.destination_structure = Archive(defined_id=defined_id,
                                             make_noid=make_noid)
        for n_segment in self.origin_structure.segment_list:
            self.destination_structure.segment_list.append(n_segment)
        for n_accessionrecord in self.origin_structure.accessionrecord_list:
            self.destination_structure.accession_record_list.append(
                n_accessionrecord
            )
        for n_legalnote in self.origin_structure.legalnote_list:
            self.destination_structure.legalnote_list.append(n_legalnote)
        for n_adminnote in self.origin_structure.adminnote_list:
            self.destination_structure.adminnote_list.append(n_adminnote)
        return self.destination_structure

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
        self._destination_structure = value

    def __repr__(self):
        return "< transform from stage {} to archive {}".\
            format(id(self.origin_structure),
                   id(self.destination_structure))

    destination_structure = property(get_destination_structure,
                                     set_destination_structure)
    origin_structure = property(get_origin_structure, set_origin_structure)
