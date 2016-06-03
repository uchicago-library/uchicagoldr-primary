
from .abc.identifiercategory import IdentifierCategory


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
