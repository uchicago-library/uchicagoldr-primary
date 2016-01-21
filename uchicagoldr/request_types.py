from uchicagoldr.request import InputType

class ProvideNewArk(InputType):
    def __init__(self):
        self.prompt = "the ark you provided is not valid. Please provide a new one."
        InputType.__init__(self, str(), validator=self._ark_validation(), prompt=self.prompt)
