from configparser import ConfigParser
from os.path import join, isfile
from xdg import BaseDirectory
from convenience import retrieve_resource_filepath

"""
This class is meant to read three potential config locations
1) A manually specified one
2) The default
3) The builtin
and provide a master parser of their output ordered by preference.
It allows the user to specify what fallbacks can be used.
"""


class ConfReader(object):
    def __init__(self, config_directory=None, config_file=None,
                 and_default=True, and_builtin=True):
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
        subparsers = [ConfigParser().read(x) for x in paths]

        # Build our master parser
        self.parser = self.mux_parsers(subparsers)

    def mux_parsers(self, ordered_subparsers):
        parser = ConfigParser()
        # Reverse the list, so when we clobber values we end up with the most
        # preferrential one
        for subparser in reversed(ordered_subparsers):
            for section in subparser:
                for value in section:
                    parser[section][value] = subparser[section][value]
        return parser

    def get_conf_value(self, key, section=None):
        if section:
            return self.parser[section][key]
        else:
            potentials = []
            for section in self.parser:
                if key in self.parser[section]:
                    potentials.append(self.parser[section][key])
            if len(potentials) < 1:
                raise KeyError(
                    "{} does not appear in any section!".format(key)
                )
            elif len(potentials) > 1:
                raise KeyError(
                    "{} appears in multiple sections, specify one!".format(key)
                )
            else:
                return potentials[0]
