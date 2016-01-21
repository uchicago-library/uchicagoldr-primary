from uchicagoldr.request import InputType

class RequestType(InputType):
    def __init__(self, prompt):
        self.prompt = prompt
        InputType.__init__(self, str(), validator=self._ark_validation(), prompt=prompt)
