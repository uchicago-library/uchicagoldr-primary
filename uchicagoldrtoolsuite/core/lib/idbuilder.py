
from .ark import Ark
from .doi import DOI


class IDBuilder(object):
    """The IDBuilder class should be used as a delegate in any class that needs
    to define an identifier for serialization.

    It returns 1 of 3 types of ids: eventId, premisID, archiveID
    """
    def __init__(self):
        """returns a subclass of the IDBuilder factory class with valid options

        1. eventID
        2. premisID
        3. archiveID
        """
        self.valid_options = ['eventID', 'premisID', 'archiveID']

    def build(self, menu_order):
        """returns an instance of a subclass of the identifier class

        __Args__
        1. menu_order (str): the type of id that is desired
        """
        if menu_order not in self.valid_options:
            raise ValueError("I don't know how to build a {} identifier".
                             format(menu_order))
        elif menu_order == 'eventID':
            output = DOI()
        elif menu_order == 'premisID':
            output = DOI()
        elif menu_order == 'archiveID':
            output = Ark()
        return output
