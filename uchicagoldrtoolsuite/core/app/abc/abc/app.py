from abc import ABCMeta, abstractmethod

from ....lib.confreader import ConfReader


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class App(metaclass=ABCMeta):
    """
    The base class for all applications

    __KWArgs__

    * __author__ (str): The author's name
    * __email__ (str): The author's email
    * __company__ (str): The author's company
    * __copyright__ (str): A copyright notice
    * __publication__ (str): A publication date (ISO8601)
    * __version__ (str): A version number
    """

    _conf = None

    def __init__(self, __author__=None, __email__=None, __company__=None,
                 __copyright__=None, __publication__=None, __version__=None):
        self.__author__ = __author__
        self.__email__ = __email__
        self.__company__ = __company__
        self.__copyright__ = __copyright__
        self.__publication__ = __publication__
        self.__version__ = __version__

    def set_conf(self, conf_dir=None, conf_filename=None, and_default=True,
                 and_builtin=True):
        self._conf = ConfReader(config_directory=conf_dir,
                                config_file=conf_filename,
                                and_default=and_default,
                                and_builtin=and_builtin
                                )

    def get_conf(self):
        return self._conf

    @abstractmethod
    def main(self):
        pass

    conf = property(get_conf, set_conf)
