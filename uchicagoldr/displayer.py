class Displayer(object):
    def __init__(self, kind, data):
        self.class_being_displayed = kind
        self.data = data

    def display(self):
        if self.class_being_displayed == 'family':
            return NotImplemented
        if self.class_being_displayed == 'directory':
            return NotImplemented
        if self.class_being_displayed == 'string':
            return NotImplemented
        if self.class_being_displayed == 'item':
            return NotImplemented
        if self.class_being_displayed == 'accessionitem':
            return NotImplemented

