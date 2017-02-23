from abc import ABCMeta

from .abc.retriever import Retriever
from .contentpointerresolver import ContentPointerResolver


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class ContentPointerRetriever(Retriever, metaclass=ABCMeta):
    """
    The abstract base class for ContentPointerRetrievers

    ContentPointerRetrievers interact with a resolver and a data source
    in order to produce a ContentPointer.
    """

    _resolver = None

    def get_resolver(self):
        return self._resolver

    def set_resolver(self, resolver):
        if not isinstance(resolver, ContentPointerResolver):
            raise ValueError('resolvers must be subclasses of ' +
                             'ContentPointerResolver')
        self._resolver = resolver

    def del_resolver(self):
        self._resolver = None

    def determine_iteration(self):
        resolution = self._resolver.resolve(self._supplied_uuid)
        return resolution.index(self._supplied_uuid)

    def is_original(self):
        resolution = self._resolver.resolve(self._supplied_uuid)
        if self._supplied_uuid == resolution[0]:
            return True
        return False

    def is_most_recent(self):
        resolution = self._resolver.resolve(self._supplied_uuid)
        if self._supplied_uuid == resolution[-1]:
            return True
        return False

    def retrieve_version(self, index):
        resolution = self._resolver.resolve(self._supplied_uuid)
        return self.retrieve(resolution[index])

    def retrieve_original(self):
        resolution = self._resolver.resolve(self._supplied_uuid)
        return self.retrieve(resolution[0])

    def retrieve_most_recent(self):
        resolution = self._resolver.resolve(self._supplied_uuid)
        return self.retrieve(resolution[-1])

    property(get_resolver, set_resolver, del_resolver)
