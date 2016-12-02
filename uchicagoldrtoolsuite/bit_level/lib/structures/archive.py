from logging import getLogger

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, \
    log_init_success
from ..ldritems.abc.ldritem import LDRItem
from .abc.accessioncontainer import AccessionContainer

__author__ = "Tyler Danstrom, Brian Balsamo"
__email__ = "tdanstrom@uchicago.edu, balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class Archive(AccessionContainer):
    """
    The structure which holds archival contents in the archive environment.
    """
    @log_aware(log)
    def __init__(self, identifier):
        """
        create a new Archive structure

        __Args__

        1. identifier (str): The identifier of the archive structure
        """
        log_init_attempt(self, log, locals())
        super().__init__(identifier)
        log_init_success(self, log)

    # TODO
    # This function actually probably belongs in a validation library, but I
    # think that might be outside of the scope of the work I'm doing in this
    # branch currently
    @log_aware(log)
    def _validate_materialsuite(self, materialsuite):
        """
        Determines a MaterialSuite is valid for inclusion in an Archive struct
        """
        log.debug("Validating MaterialSuite for inclusion in an Archive")
        try:
            if not isinstance(materialsuite.content, LDRItem) and \
                    not isinstance(materialsuite.content, type(None)):
                log.warn("Incorrect object (not LDRItem or None) in a " +
                         "MaterialSuite content slot")
                return False
            if not isinstance(materialsuite.premis, LDRItem):
                log.warn("MaterialSuite missing PREMIS metadata")
                return False
            # TODO: Decide if mandating technical metadata (when there's
            # content) is a solid idea, is this an implementation specific
            # detail?
            if not len(materialsuite.technicalmetadata_list) > 0 and \
                    isinstance(materialsuite.content, LDRItem):
                log.warn("Content exists with no technical metadata")
                return False
        except Exception:
            log.critical("Problem in MaterialSuite validation")
            return False
        return True

    @log_aware(log)
    def validate(self):
        """
        Determines if the structure includes all the required components
        and that they are all well formed.
        """
        log.info("Validating included components")
        for materialsuite in self.materialsuite_list:
            if self._validate_materialsuite(materialsuite) is False:
                log.warn("A MaterialSuite is malformed")
                return False
        if len(self.accessionrecord_list) < 1:
            log.warn("Missing an accession record")
            return False
        return True
