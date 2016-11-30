from logging import getLogger

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.ark import Ark
from .abc.transformer import Transformer
from ..structures.archive import Archive
from ..structures.stage import Stage
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, log_init_success

__author__ = "Tyler Danstrom, Brian Balsamo"
__email__ = " tdanstrom@uchicago.edu, balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class StageToArchiveTransformer(Transformer):
    """The StageToARrchiveTransformer takes an instance of a Stage structure
    and copies its contents into an instance of an Archive structure
    """
    @log_aware(log)
    def __init__(self, origin_structure):
        """instantiates an instance of a StageToArrchiveTansformer

        It starts with the origin structure passed as a parameter
        and sets an empty destination structure.

        ___Args__
        1. origin_structure (Stage) : a fully realized instance of a
        Stage structure
        """
        log_init_attempt(self, log, locals())
        self.origin_structure = origin_structure
        self.destination_structure = None
        log_init_success(self, log)

    @log_aware(log)
    def transform(self, archive_identifier=None, noid_minter_url=None):
        """returns a fully realized Archive structure containing the contents
        of the origin Stage structure.

        It copies the contents of the Stage structure into the new Archive structure
        and sets the data attribute destination_structure before returning said
        destination structure data attribute value.
        """
        log.info("Transforming a Stage into an equivalent Archive")
        if self.destination_structure is not None:
            raise TypeError("a transformation already occured.")
        if archive_identifier == noid_minter_url == None:
            raise RuntimeError("An identifier must be explicitly provided " +
                               "or the URL of a noid minter must be provided.")
        if archive_identifier is None:
            log.debug("No Archive identifier provided, minting a noid")
            archive_identifier = Ark(noid_minter_url).value
        self.destination_structure = Archive(archive_identifier)

        log.debug("Adding segments to the Archive")
        for n_segment in self.origin_structure.segment_list:
            self.destination_structure.add_segment(
                n_segment
            )

        log.debug("Adding accession records to the Archive")
        for n_accessionrecord in self.origin_structure.accessionrecord_list:
            self.destination_structure.add_accessionrecord(
                n_accessionrecord
            )

        log.debug("Adding legalnotes to the Archive")
        for n_legalnote in self.origin_structure.legalnote_list:
            self.destination_structure.add_legalnote(
                n_legalnote
            )

        log.debug("Adding adminnotes to the Archive")
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
        if isinstance(value, Stage):
            self._origin_structure = value
        else:
            raise ValueError("StageToPairtreeTransformer must have an " +
                             "instace of a Stage in origin_structure")

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
        return "< transform from stage {} to archive {}".\
            format(id(self.origin_structure),
                   id(self.destination_structure))

    destination_structure = property(get_destination_structure,
                                     set_destination_structure)
    origin_structure = property(get_origin_structure, set_origin_structure)
