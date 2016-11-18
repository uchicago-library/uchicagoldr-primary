from uuid import uuid4
from logging import getLogger

from uchicagoldrtoolsuite import log_aware
from .abc.transformer import Transformer
from ..structures.archive import Archive
from ..structures.stage import Stage

__author__ = "Tyler Danstrom, Brian Balsamo"
__email__ = " tdanstrom@uchicago.edu, balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class ArchiveToStageTransformer(Transformer):
    """The StageToARrchiveTransformer takes an instance of a Stage structure
    and copies its contents into an instance of an Archive structure
    """
    @log_aware(log)
    def __init__(self, origin_structure):
        """instantiates an instance of a StageToARrchiveTansformer

        It starts with the origin structure passed as a parameter
        and sets an empty destination structure.

        ___Args__
        1. origin_structure (Archive) : a fully realized instance of a
        Archive structure
        """
        self.origin_structure = origin_structure
        self.destination_structure = None

    @log_aware(log)
    def transform(self, stage_identifier=None):
        """returns a fully realized Archive structure containing the contents
        of the origin Stage structure.

        It copies the contents of the Stage structure into the new Archive structure
        and sets the data attribute destination_structure before returning said
        destination structure data attribute value.
        """
        if self.destination_structure is not None:
            raise TypeError("a transformation already occured.")
        if stage_identifier is None:
            stage_identifier = uuid4().hex
        self.destination_structure = Stage(stage_identifier)

        for n_segment in self.origin_structure.segment_list:
            self.destination_structure.add_segment(
                n_segment
            )

        for n_accessionrecord in self.origin_structure.accessionrecord_list:
            self.destination_structure.add_accessionrecord(
                n_accessionrecord
            )

        for n_legalnote in self.origin_structure.legalnote_list:
            self.destination_structure.add_legalnote(
                n_legalnote
            )

        for n_adminnote in self.origin_structure.adminnote_list:
            self.destination_structure.add_adminnote(
                n_adminnote
            )

        return self.destination_structure

    @log_aware(log)
    def get_origin_structure(self):
        """returns the origin structure, in this case a fully-realized Stage structure
        """
        return self._origin_structure

    @log_aware(log)
    def set_origin_structure(self, value):
        """sets the origin structure: it will only accept a Stage structure
        """
        if isinstance(value, Archive):
            self._origin_structure = value
        else:
            raise ValueError("ArchiveToStageTransformerr must have an " +
                             "instace of an Archive in origin_structure")

    @log_aware(log)
    def get_destination_structure(self):
        """returns the destination structure, or the structure created from transform method
        """
        return self._destination_structure

    @log_aware(log)
    def set_destination_structure(self, value):
        """sets the destination structure, an Archive structure
        """
        self._destination_structure = value

    @log_aware(log)
    def __repr__(self):
        return "< transform from archive {} to stage {}".\
            format(id(self.origin_structure),
                   id(self.destination_structure))

    destination_structure = property(get_destination_structure,
                                     set_destination_structure)
    origin_structure = property(get_origin_structure, set_origin_structure)
