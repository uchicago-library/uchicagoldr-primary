from configparser import ConfigParser
from os.path import join, isfile
from xdg import BaseDirectory
from uchicagoldrtoolsuite.lib.convenience import retrieve_resource_filepath


class ConfReader(object):
    """
    This class is meant to read three potential config locations
    1) A manually specified one
    2) The default
    3) The builtin
    and provide a master parser of their output ordered by preference.
    It allows the user to specify what fallbacks can be used.

    The majority of its methods are simple passthroughs to ConfigParser

    __Attribs__

    * self.parser (ConfigParser): The internal parser
    """
    def __init__(self, config_directory=None, config_file=None,
                 and_default=True, and_builtin=True):
        """
        Build a new ConfReader to read values from

        __KWArgs__

        * config_directory (str): A path to a manually specified config dir
        * config_file (str): The filename of a primary conf in that dir
        defaults to "ldr.ini"
        * and_default (bool): Whether or not to check/use the default
        conf location
        * and_builtin (bool): Whether or not to check/use the builtin conf
        """
        # Assume if the user didn't enter a filename they used the default
        if config_file is None:
            config_file = 'ldr.ini'

        # Look in a user specified location
        if config_directory:
            user_specified_config_path = join(config_directory, config_file)
        else:
            user_specified_config_path = None

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

        # Filter out None's and things that aren't files
        paths = [user_specified_config_path,
                 default_config_path,
                 builtin_config_path]
        paths = [x for x in paths if x is not None]
        paths = [x for x in paths if isfile(x)]

        # Build a parser from each one
        subparsers = []
        for x in paths:
            subparser = ConfigParser()
            with open(x, 'r') as f:
                subparser.read_file(f)
            subparsers.append(subparser)

        # Build our master parser
        self.parser = self.mux_parsers(subparsers)

    def __getitem__(self, key):
        return self.parser.__getitem__(key)

    def __setitem__(self, key, value):
        return self.parser__setitem__(key, value)

    def __missing__(self, key):
        return self.parser.__missing__(key)

    def __delitem__(self, key):
        return self.parser.__delitem__(key)

    def __len__(self):
        return self.parser.__len__()

    def __iter__(self):
        return self.parser.__iter__()

    def __reversed__(self):
        return self.parser.__reversed__()

    def __contains__(self, item):
        return self.parser.__contains__(item)

    def mux_parsers(self, ordered_subparsers):
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
                    parser[section][option] = subparser.get(section, option, raw=True)

        return parser

    def get(self, *args, **kwargs):
        """
        see ConfigParser.get
        """
        return self.parser.get(*args, **kwargs)

    def getint(self, *args, **kwargs):
        """
        see ConfigParser.getint
        """
        return self.parser.getint(*args, **kwargs)

    def getfloat(self, *args, **kwargs):
        """
        see ConfigParser.getfloat
        """
        return self.parser.getfloat(*args, **kwargs)

    def getboolean(self, *args, **kwargs):
        """
        see ConfigParser.getbool
        """
        return self.parser.getbool(*args, **kwargs)

    def defaults(self):
        """
        see ConfigParser.defaults
        """
        return self.parser.defaults()

    def sections(self):
        """
        see ConfigParser.sections
        """
        return self.parser.sections()

    def add_section(self, *args):
        """
        see ConfigParser.add_section
        """
        return self.parser.add_section(*args)

    def has_section(self, *args):
        """
        see ConfigParser.has_section
        """
        return self.parser.has_section(*args)

    def options(self, *args):
        """
        see ConfigParser.options
        """
        return self.parser.options(*args)

    def read(self, *args, **kwargs):
        """
        see ConfigParser.read
        """
        return self.parser.read(*args, **kwargs)

    def read_file(self, *args, **kwargs):
        """
        see ConfigParser.read_file
        """
        return self.parser.read_file(*args, **kwargs)

    def read_string(self, *args, **kwargs):
        """
        see ConfigParser.read_string
        """
        return self.parser.read_string(*args, **kwargs)

    def read_dict(self, *args, **kwargs):
        """
        see ConfigParser.read_dict
        """
        return self.parser.read_dict(*args, **kwargs)

    def items(self, *args, **kwargs):
        """
        see ConfigParser.items
        """
        return self.parser.items(*args, **kwargs)

    def set(self, *args):
        """
        see ConfigParser.set
        """
        return self.parser.set(*args)

    def write(self, *args, **kwargs):
        """
        see ConfigParser.write
        """
        return self.parser.write(*args, **kwargs)

    def remove_option(self, *args):
        """
        see ConfigParser.remove_option
        """
        return self.parser.remove_option(*args)

    def remove_section(self, *args):
        """
        see ConfigParser.remove_section
        """
        return self.parser.remove_sectin(*args)

    def optionxform(self, *args):
        """
        see ConfigParser.optionxform
        """
        return self.parser.optionxform(*args)

    def readfp(self, *args, **kwargs):
        """
        see ConfigParser.readfp
        """
        return self.parser.readfp(*args, **kwargs)
