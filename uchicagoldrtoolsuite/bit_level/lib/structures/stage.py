from logging import getLogger

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, \
    log_init_success
from .abc.accessioncontainer import AccessionContainer


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class Stage(AccessionContainer):
    """
    A Stage is a structure which holds an aggregates contents
    as they are being processed for ingestion into long term storage
    """
    @log_aware(log)
    def __init__(self, identifier):
        """
        Creates a new Stage

        __Args__

        param1 (str): The identifier that will be assigned to the Stage
        """
        log_init_attempt(self, log, locals())
        super().__init__(identifier)
        log_init_success(self, log)
