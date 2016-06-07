
from uuid import uuid1

from .identifier import Identifier


class DOI(Identifier):
    def __init__(self):
        super().__init__('doi')
        self.value = self.generate()

    def generate(self):
        return uuid1().hex

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = value

    value = property(get_value, set_value)
