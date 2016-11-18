from urllib.request import urlopen, URLError
from configparser import NoOptionError
from logging import getLogger

from requests import get
from requests.exceptions import SSLError

from uchicagoldrtoolsuite.core.lib.confreader import ConfReader
from .identifier import Identifier


__author__ = "Tyler Danstrom, Brian Balsamo"
__email__ = " tdanstrom@uchicago.edu, balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class Ark(Identifier):
    """Is a LDR version of a DOI identifier. The identifer value is a uuid1
    the category is DOI
    """
    def __init__(self, noid_minter_url=None):
        """returns a DOI identifer subclass
        It calls the init for the super class identifier to set the category
        """
        super().__init__('noid')
        if noid_minter_url is None:
            try:
                noid_minter_url = ConfReader().get("URLs", "noid_minter")
            except NoOptionError:
                raise ValueError("No noid_minter_url provided. Provide " +
                                 "a url via a kwarg or a conf value.")
        self.value = self.generate(noid_minter_url)
        log.debug("Spawned an ARK: {}".format(str(self)))

    def __repr__(self):
        attr_dict = {
            'category': self.category,
            'value': str(self.value)
        }
        return "<Ark {}>".format(attr_dict)

    def generate(self, noid_minter_url):
        """returns a noid instance as an ascii string
        """
        try:
            response = get(noid_minter_url)
        except SSLError:
            response = get(noid_minter_url, verify=False)
            log.warn("Bad SSL Cert @ {}".format(noid_minter_url))
        if response.status_code == 200:
            data = response.text
            data_output = data.split('61001/')[1].rstrip()
        else:
            raise URLError("Cannot read noid minter located at {}".format(
                noid_minter_url))
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
