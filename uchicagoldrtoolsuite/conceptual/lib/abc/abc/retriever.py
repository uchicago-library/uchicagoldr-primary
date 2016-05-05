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

    __Attribs__

    * _supplied_uuid (str): The supplied uuid to retrieve

    __Methods__

    * _set_supplied_uuid(str): Set the supplied uuid
        * this should almost assuredly be called in every concrete classes
        init

    * _get_supplied_uuid(): Returns the supplied uuid value

    __Abstract Methods__

    * retrieve(): Retrieves the supplied uuid
    """

    _supplied_uuid = None

    @abstractmethod
    def retrieve(self uuid=None):
        pass

    def _set_supplied_uuid(self, uuid):
        if not isinstance(uuid, str):
            raise ValueError("Supplied uuids must be strings")
        self._supplied_uuid = uuid

    def _get_supplied_uuid(self):
        return self._supplied_uuid

    property(_get_supplied_uuid, _set_supplied_uuid)
