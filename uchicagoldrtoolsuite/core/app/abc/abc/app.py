from abc import ABCMeta, abstractmethod
from configparser import ConfigParser
from os.path import join, isfile
from xdg import BaseDirectory

from uchicagoldrtoolsuite import retrieve_resource_filepath


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

    @abstractmethod
    def main(self):
        pass

    @staticmethod
    def mux_parsers(ordered_subparsers):
        """
        mux together a list of parsers, ordered from most preferred to least

        __Args__

        1) ordered_subparsers (list): The other parsers, ordered from
        most preferred to least

        __Returns__

        * parser (ConfigParser): A parser containing the final values
        """
        parser = ConfigParser()
        # Reverse the list, so when we clobber values we end up with the most
        # preferrential one
        for subparser in reversed(ordered_subparsers):
            for section in subparser.sections():
                for option in subparser.options(section):
                    if not parser.has_section(section):
                        parser.add_section(section)
                    parser[section][option] = subparser.get(section, option,
                                                            raw=True)
        return parser

    @classmethod
    def build_conf(cls, user_specified=None,
                   and_default=True, and_builtin=True):
        """
        build and return new conf

        __KWArgs__

        * config_directory (str): A path to a manually specified config dir
        * config_file (str): The filename of a primary conf in that dir
        defaults to "ldr.ini"
        * and_default (bool): Whether or not to check/use the default
        conf location
        * and_builtin (bool): Whether or not to check/use the builtin conf
        """
        # Look in the default location, if we can
        if and_default:
            default_dir = join(BaseDirectory.xdg_config_home, 'ldr')
            default_file = 'ldr.ini'
            default_config_path = join(default_dir, default_file)
        else:
            default_config_path = None

        # Look for the builtin configs, if we can
        if and_builtin:
            builtin_config_path = retrieve_resource_filepath('configs/ldr.ini')
        else:
            builtin_config_path = None

        paths = [x for x in user_specified]
        paths.append(default_config_path)
        paths.append(builtin_config_path)
        # Filter out None's and things that aren't files
        paths = [x for x in paths if x is not None and isfile(x)]

        # Build a parser from each one
        subparsers = []
        for x in paths:
            subparser = ConfigParser()
            with open(x, 'r') as f:
                subparser.read_file(f)
            subparsers.append(subparser)

        # Build our master parser
        return cls.mux_parsers(subparsers)

    def get_conf(self):
        return self._conf

    def set_conf(self, x):
        self._conf = x

    conf = property(get_conf, set_conf)
