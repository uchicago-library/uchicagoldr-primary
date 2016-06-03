
from uuid import uuid1

from .identifier import Identifier


class DOI(Identifier):
    """Is a LDR version of a DOI identifier. The identifer value is a uuid1
    the cateeogry is DOI
    """
    def __init__(self):
        """returns a DOI identifer subclass
        It calls the init for the super class identifier to set the category
        """
        super().__init__('doi')
        self.value = self.generate()

    def generate(self):
        """returns a uuid1 instance as a hexdigest string
        """
        return uuid1().hex

    def get_value(self):
        """returns the identifier value of the DOI object instance
        """
        return self._value

    def set_value(self, value):
        """sets the identifier value for the DOI object
        """
        self._value = value

    value = property(get_value, set_value)
