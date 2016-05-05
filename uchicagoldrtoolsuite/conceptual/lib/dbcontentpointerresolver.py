from .contentpointerresolver import ContentPointerResolver
from .dbenvmixin import DatabaseEnvironmentMixin


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class DatabaseContentPointerResolver(DatabaseEnvironmentMixin,
                                     ContentPointerResolver):
    def __init__(self):
        pass

    def resolve(self, uuid):
        pass
