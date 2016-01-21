from uchicagoldr.request import InputType

class ProvideNewArk(InputType):
    def __init__(self):
        self.prompt = "the ark you provided is not valid. Please provide a new one."
        InputType.__init__(self, str(), validator=self._ark_validation(), prompt=self.prompt)

class MissingSourceDirectory(InputType):
    def __init__(self):
        self.prompt = "the source directory you entered does not exist."
        InputType.__init__(self, str(), validator=self._ark_validation(), prompt=self.prompt)

class MissingDestinationDirectory(InputType):
    def __init__(self):
        self.prompt = "the destination directory you entered does not exist."
        InputType.__init__(self, str(), validator=self._ark_validation(), prompt=self.prompt)

class CollissionProblem(InputType):
    def __init__(self,collisions):
        self.prompt = "there was a collision between the following files".format(', '.join(collisions)
        InputType.__init__(self, str(), validator=self._ark_validation(), prompt=self.prompt)                
