
from urllib.request import urlopen, URLError

from .identifier import Identifier

__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class Ark(Identifier):
    """Is a LDR version of a DOI identifier. The identifer value is a uuid1
    the cateeogry is DOI
    """
    def __init__(self):
        """returns a DOI identifer subclass
        It calls the init for the super class identifier to set the category
        """
        super().__init__('noid')
        self.value = self.generate()

    def generate(self):
        """returns a noid instance as an ascii string
        """
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
        """returns the identifier value of the DOI object instance
        """
        return self._value

    def set_value(self, value):
        """sets the identifier value for the DOI object
        """
        self._value = value

    value = property(get_value, set_value)
