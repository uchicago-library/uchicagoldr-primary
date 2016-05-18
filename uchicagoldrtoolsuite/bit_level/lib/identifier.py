
from .abc.identifiercategory import IdentifierCategory


class Identifier(IdentifierCategory):
    def __init__(self, category):
        self.category = category

    def show(self):
        return (self.category, self.value)
