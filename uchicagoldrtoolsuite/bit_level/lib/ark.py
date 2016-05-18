
from urllib.request import urlopen, URLError

from .identifier import Identifier


class Ark(Identifier):
    def __init__(self):
        super().__init__('noid')
        self.value = self.generate()

    def generate(self):
        request = urlopen("https://y1.lib.uchicago.edu/" +
                          "cgi-bin/minter/noid?action=mint&n=1")
        if request.status == 200:
            data = request.readlines()
            data_output = data.decode('utf-8').split('61001/')[1].rstrip()
        else:
            raise URLError("Cannot read noid minter located at" +
                           "https://y1.lib.uchicago.edu/cgi-bin/minter/" +
                           "noid?action=mint&n=1")
        return data_output

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = value

    value = property(get_value, set_value)
