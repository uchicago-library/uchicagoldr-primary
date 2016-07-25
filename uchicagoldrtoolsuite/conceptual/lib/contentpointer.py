from uuid import uuid1

__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class ContentPointer(object):
    """
    A content pointer is the leaf element of the conceptual processing side
    it is a reference to some content, independant of the file that content
    now resides in or the **exact** nature of that content. In combination with
    a resolver it facilitates retrieving any existing version of content.

    __Attribs__

    * _identifier: a uuid
    """

    _identifier = None

    def __init__(self, identifier):
        """
        Initialize a new content pointer

        __KWArgs__

        * identifier (str): An identifier to embed in the object
        """
        self.identifier = identifier
        if self._identifier is None:
            self._identifier = str(uuid1())

    def __hash__(self):
        return hash(self.get_identifier())

    def __eq__(self, other):
        return (isinstance(other, ContentPointer) and
                hash(self) == hash(other))

    def __repr__(self):
        return "ContentPointer object with identifer {}".format(self.get_identifier())

    def get_identifier(self):
        """
        return the object identifier

        __Returns__

        * (str): the identifier.
        """
        return self._identifier

    def set_identifier(self, identifier):
        if not isinstance(identifier, str):
            raise ValueError("Identifiers should be strings.")
        self._identifier = identifier

    identifier = property(get_identifier, set_identifier)
