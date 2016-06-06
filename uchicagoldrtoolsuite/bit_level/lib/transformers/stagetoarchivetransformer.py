
from ..structures.archive import Archive
from .abc.transformer import Transformer
from ..structures.stage import Stage

__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class StageToArchiveTransformer(Transformer):
    """The StageToARrchiveTransformer takes an instance of a Stage structure
    and copies its contents into an instance of an Archive structure
    """
    def __init__(self, origin_structure):
        """instantiates an instance of a StageToARrchiveTansformer
        
        It starts with the origin structure passed as a parameter
        and sets an empty destination structure.

        ___Args__
        1. origin_structure (Stage) : a fully realized instance of a 
        Stage structure
        """
        self.origin_structure = origin_structure
        self.destination_structure = None

    def transform(self, defined_id=None, make_noid=False):
        """returns a fully realized Archive structure containing the contents
        of the origin Stage structure.

        It copies the contents of the Stage structure into the new Archive structure
        and sets the data attribute destination_structure before returning said
        destination structure data attribute value.
        """
        if self.destination_structure is not None:
            raise TypeError("a transformation already occured.")
        self.destination_structure = Archive(
            defined_id=defined_id,
            make_noid=make_noid
        )
        for n_segment in self.origin_structure.segment_list:
            self.destination_structure.segment_list.append(
                n_segment
            )
        for n_accessionrecord in self.origin_structure.accessionrecord_list:
            self.destination_structure.accessionrecord_list.append(
                n_accessionrecord
            )
        for n_legalnote in self.origin_structure.legalnote_list:
            self.destination_structure.legalnote_list.append(
                n_legalnote
            )
        for n_adminnote in self.origin_structure.adminnote_list:
            self.destination_structure.adminnote_list.append(
                n_adminnote
            )
        return self.destination_structure

    def get_origin_structure(self):
        """returns the origin structure, in this case a fully-realized Stage structure
        """
        return self._origin_structure

    def set_origin_structure(self, value):
        """sets the origin structure: it will only accept a Stage structure
        """
        if isinstance(value, Stage):
            self._origin_structure = value
        else:
            raise ValueError("StageToPairtreeTransformer must have an " +
                             "of a Stage in origin_structure")

    def get_destination_structure(self):
        """returns the destination structure, or the structure created from transform method
        """
        return self._destination_structure

    def set_destination_structure(self, value):
        """sets the destination structure, an Archive structure
        """
        self._destination_structure = value

    def __repr__(self):
        return "< transform from stage {} to archive {}".\
            format(id(self.origin_structure),
                   id(self.destination_structure))

    destination_structure = property(get_destination_structure,
                                     set_destination_structure)
    origin_structure = property(get_origin_structure, set_origin_structure)
