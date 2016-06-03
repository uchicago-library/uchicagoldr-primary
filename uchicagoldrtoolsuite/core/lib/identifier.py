
from .abc.identifiercategory import IdentifierCategory

__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class Identifier(IdentifierCategory):
    """the identifier class is a superclass for identifier types
    """

    def __init__(self, category):
        """ creates an instance of the identifier class

        __Args__
        1. category (str): the type of identifier that is being created.
        This should be a identifier standard like DOI or URN
        """
        self.category = category.upper()

    def show(self):
        """returns a tuple containing the category and the identifier value
        of an instance of the identifier class
        """
        return (self.category, self.value)
