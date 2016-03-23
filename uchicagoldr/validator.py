
class Validator(object):
    def __init__(self, order):
        self.order = order

    def test(self):
        return False

    def verbose_test(self) -> str:
        return "not implemented"
