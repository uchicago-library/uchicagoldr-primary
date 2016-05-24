
from .ark import Ark
from .doi import DOI


class IDBuilder(object):
    def __init__(self):
        self.valid_options = ['eventID', 'premisID', 'archiveID']

    def build(self, menu_order):
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
