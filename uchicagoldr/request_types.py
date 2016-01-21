from uchicagoldr.request import *

class RequestType(Request):
    def __init__(self, prompt):
        self.prompt = prompt
        Request.__init__(self, str(), validator=self._ark_validation(), prompt=prompt)
