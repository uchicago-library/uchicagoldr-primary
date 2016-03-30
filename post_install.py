from argparse import ArgumentParser
from os.path import join, split, exists, \
    expanduser, expandvars, normpath, realpath
from os import makedirs
from xdg import BaseDirectory
from configparser import ConfigParser

__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "University of Chicago"
__copyright__ = "University of Chicago, 2016"
__version__ = "0.0.1"


class CLIInput(object):
    def __init__(self, disptext, default=None):
        self.disptext = disptext
        self.default = default
        self.answer = None

    def prompt(self):
        if not self.default:
            return input("{}: ".format(self.disptext))
        else:
            return input("{} ({}): ".format(self.disptext, self.default))

    def get_input(self):
        x = self.prompt()
        if x == '':
            if self.default:
                return self.default
            else:
                return None
        return x


class YNCLIInput(CLIInput):
    def __init__(self, disptext, default=None):
        disptext = disptext+" [y/n]"
        CLIInput.__init__(self, disptext, default)

    def get_input(self):
        i = CLIInput.get_input(self).lower()
        if i.lower() != 'y' and \
                i != 'yes' and \
                i != 'n' and \
                i != 'no':
            print('Invalid Input')
            return self.get_input()

        if i == 'y' or i == 'yes':
            return True
        else:
            return False


class PathCLIInput(CLIInput):
    def get_input(self):
        i = CLIInput.get_input(self)
        return realpath(normpath(expanduser(expandvars(i))))


def create_prompt(path, dir_or_file):
    if not exists(path):
        i = YNCLIInput(
            '{} does not exist on the filesystem. Create it?'.format(path),
            default='y'
        ).get_input()
        if i:
            if dir_or_file == 'dir':
                makedirs(path)
            elif dir_or_file == 'file':
                makedirs(split(path)[0])
                open(split(path)[1], 'w').close()
            else:
                raise AssertionError()
        else:
            return False
    else:
        return True


def populate_conf_dir(conf_dir):
    pass


def first_conf_setup():
    conf_dir_suggest = join(BaseDirectory.xdg_config_home, 'ldr')
    conf_dir = PathCLIInput(
        'Config directory location', default=conf_dir_suggest
    ).get_input()
    while not create_prompt(conf_dir, 'dir'):
        create_prompt(conf_dir, 'dir')
    populate_conf_dir(conf_dir)

    print('Your configuration directory is located at: {}'.format(conf_dir))


def main():
    # arg parser instantiation
    parser = ArgumentParser(description="this is the initial configuration " +
                            "script for the University of Chicago " +
                            "Library Digital Repository Tool Suite.")

    args = parser.parse_args()

    # app code
    print('Welcome to the University of Chicago Library Digital ' +
          'Repository Tool Suite configuration wizard.')
    print('This configuration wizard will walk you through creating ' +
          'the initial required environment for the tool suite by ' +
          'suggesting sensible default values for certain configuration ' +
          'options and automatically installing some templates.')
    print()
    print('This wizard will prompt you for a variety of values, sometimes ' +
          'provide suggested defaults (displayed in parenthesis). To accept ' +
          'a default value you need only hit enter, to provide a new value ' +
          'type it when prompted')
    print()
    print('If you are presented with choices, valid inputs will be displayed ' +
          'in square brackets.')
    print()
    print('At any time you may exit this wizard by hitting Ctrl+c')
    print()
    print('To begin, lets determine a location for your configuration ' +
          'directory.')

    first_conf_setup()

if __name__ == '__main__':
    main()
