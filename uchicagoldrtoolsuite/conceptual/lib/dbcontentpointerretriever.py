from .abc.contentpointerretriever import ContentPointerRetriever
from .dbenvmixin import DatabaseEnvironmentMixin
from .dbcontentpointerresolver import DatabaseContentPointerResolver

__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class DatabaseContentPointerRetriever(DatabaseEnvironmentMixin,
                                      ContentPointerRetriever):
    def __init__(self, resolver=None):
        if resolver:
            self.set_resolver(resolver)

    def retrieve(self, uuid=None):
        if uuid is None:
            uuid = self._get_supplied_uuid()
        # more stuff
        pass
