from abc import ABCMeta, abstractmethod

__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class ContentPointerResolver(metaclass=ABCMeta):
    """
    The abstract base class for all content pointer resolvers.

    ContentPointerResolvers interact with a data location in order
    to provide an ordered list of identifiers representing versions
    of the same content.

    __Attribs__

    * None

    __Methods__

    * None

    __Abstract Methods__

    * resolve(str): list
        * provides no functinality via super
    """

    @abstractmethod
    def resolve(self, uuid):
        """
        mandates the resolve() method be implemented in concrete subclasses.
        """
        pass
