from .abc.familyretriever import FamilyRetriever
from .dbenvmixin import DatabaseEnvironmentMixin

__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class DatabaseFamilyRetriever(DatabaseEnvironmentMixin,
                              FamilyRetriever):
    def __init__(self):
        pass

    def retrieve(self, uuid=None):
        if uuid is None:
            uuid = self._get_supplied_uuid()
        # more stuff
        pass
