from abc import ABCMeta, abstractmethod


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class Retriever(metaclass=ABCMeta):
    """
    The abstract base class for all retrievers.

    Retrievers interact with a data location in order to return objects.

    __Abstract Methods__

    * retrieve(): Retrieves the supplied uuid
    """

    @abstractmethod
    def retrieve(self, request):
        if not self.verify_request(request):
            raise ValueError("Unverified request!")
        pass

    @abstractmethod
    def verify_request(self, r):
        pass

    @abstractmethod
    def get_premis(self, uuid):
        pass

    @abstractmethod
    def get_content(self, uuid):
        pass

    @abstractmethod
    def get_techmd(self, uuid, index=0):
        pass
