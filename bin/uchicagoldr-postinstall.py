from argparse import ArgumentParser
from os.path import join, split, exists, \
    expanduser, expandvars, normpath, realpath
from os import makedirs
from xdg import BaseDirectory
from configparser import ConfigParser
from uchicagoldr.convenience import retrieve_resource_str

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
                return True
            elif dir_or_file == 'file':
                try:
                    makedirs(split(path)[0])
                except FileExistsError:
                    pass
                open(path, 'w').close()
                return True
            else:
                raise AssertionError()
        else:
            return False
    else:
        print("{} already exists, and has not been clobbered.".format(path))
        return True


def first_conf_dir_setup():
    conf_dir_suggest = join(BaseDirectory.xdg_config_home, 'ldr')
    conf_dir = PathCLIInput(
        'Config directory location', default=conf_dir_suggest
    ).get_input()
    conf_created = create_prompt(conf_dir, 'dir')
    if not conf_created:
        print('Configuration can not continue without a target directory. Exiting.')
        exit(1)

    print('Your configuration directory is located at: {}'.format(conf_dir))
    return conf_dir


def first_conf_file_setup(conf_dir):
    conf_file_suggest = join(conf_dir, 'ldr.ini')
    conf_file = PathCLIInput(
        'Primary config file location', default=conf_file_suggest
    ).get_input()
    conf_created = create_prompt(conf_file, 'file')
    if not conf_created:
        print('You have chosen not to create a configuration file. System ' +
              'defaults will be used.')
        return None
    print("Populating config with template...")
    default_conf = retrieve_resource_str('configs/ldr.ini')
    with open(conf_file, 'w') as f:
        for line in default_conf.split('\n'):
            f.write("#"+line+'\n')


def main():
    # arg parser instantiation
    parser = ArgumentParser(description="this is the initial configuration " +
                            "script for the University of Chicago " +
                            "Library Digital Repository Tool Suite.")
    parser.add_argument('-x', '--x',
                        action='store_true',
                        default=False)

    args = parser.parse_args()

    # app code
    if args.x:
        print("0000000000000000000000000000000000000")
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
    conf_dir = first_conf_dir_setup()
    print()
    print('We will now populate your configuration directory with some ' +
          'default files. Values set in your user config will override ' +
          'values in the global config. The global config is located ' +
          'inside of the python package. Changing them there and ' +
          'recompiling the package will set global defaults.')
    conf_file = first_conf_file_setup(conf_dir)

if __name__ == '__main__':
    main()
