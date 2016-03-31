from argparse import ArgumentParser
from os.path import join, split, exists, \
    expanduser, expandvars, normpath, realpath
from os import makedirs
from shutil import copyfile
from xdg import BaseDirectory
from configparser import ConfigParser
from uchicagoldr.convenience import retrieve_resource_str, \
    retrieve_resource_filepath

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
    if len(open(conf_file, 'r').read()) == 0:
        print("Populating config with template...")
        default_conf = retrieve_resource_str('configs/ldr.ini')
        with open(conf_file, 'w') as f:
            for line in default_conf.split('\n'):
                f.write("#"+line+'\n')
        return conf_file
    else:
        print("Your conf file appears to already contain data. It is not " +
              "being overwritten.")
        return conf_file


def migrate_cvs(conf_dir):
    print('The UChicago LDR utilizes several built-in controlled ' +
          'vocabularies. You may edit these vocabularies (or create ' +
          'new vocabularies) in order to change how certain tools behave.')
    if YNCLIInput('Would you like to copy user-editable versions of these ' +
                  'vocabularies to a location?', default='y').get_input():
        vocabs_list = ['controlledvocabs/filepaths_fits.json',
                       'controlledvocabs/filepaths_premis.json',
                       'controlledvocabs/filepaths_presform.json',
                       'controlledvocabs/restriction_codes.json']
        cv_path = PathCLIInput('Please specify a directory to copy the ' +
                               'controlled vocabulary files to',
                               default=join(conf_dir, 'controlledvocabs')).get_input()
        cv_path_created = create_prompt(cv_path, 'dir')
        if cv_path_created:
            for x in vocabs_list:
                f_exists = exists(join(cv_path, split(x)[1]))
                if f_exists:
                    f_hasdata = len(open(join(cv_path, split(x)[1]), 'r').read()) > 0
                else:
                    f_hasdata = False
                if f_hasdata:
                    print("{} exists ".format(join(cv_path, split(x)[1])) +
                          "and contains data, it is not being clobbered.")
                else:
                    copyfile(retrieve_resource_filepath(x), join(cv_path, split(x)[1]))
        return cv_path
    else:
        print('Controlled vocabularies not copied - builtin vocabularies ' +
              'will be utilized unless otherwise specified in the config.')
        return None


def migrate_records(conf_dir):
    print('The Uchicago LDR utilizes several built-in record configurations ' +
          'to control record layouts. You may edit these configurations ' +
          '(or create new ones) in order to change how certain tools behave.')
    if YNCLIInput('Would you like to copy user-editable versions of these ' +
                  'configurations to a location?', default='y').get_input():
        configs_list = ['record_configs/AccessionRecordFields.csv']
        rc_path = PathCLIInput('Please specify a directory to copy the ' +
                               'record configuration files to',
                               default=join(conf_dir, 'record_configs')).get_input()
        rc_path_created = create_prompt(rc_path, 'dir')
        if rc_path_created:
            for x in configs_list:
                f_exists = exists(join(rc_path, split(x)[1]))
                if f_exists:
                    f_hasdata = len(open(join(rc_path, split(x)[1]), 'r').read()) > 0
                else:
                    f_hasdata = False
                if f_hasdata:
                    print("{} exists ".format(join(rc_path, split(x)[1])) +
                          "and contains data, it is not being clobbered.")
                else:
                    copyfile(retrieve_resource_filepath(x), join(rc_path, split(x)[1]))
        return rc_path
    else:
        print('Record Configurations not copied - builtin vocabularies ' +
              'will be utilized unless otherwise specified in the config.')
        return None


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
    conf_dir = first_conf_dir_setup()
    print()
    print('We will now populate your configuration directory with some ' +
          'default files. Values set in your user config will override ' +
          'values in the global config. The global config is located ' +
          'inside of the python package. Changing them there and ' +
          'recompiling the package will set global defaults.')
    conf_file = first_conf_file_setup(conf_dir)
    print()
    print('We will now determine the location for user editable controlled ' +
          'vocabularies, if any')
    cvs_dir = migrate_cvs(conf_dir)
    print()
    print('We will now determine the location for the user editable record ' +
          'configuration files, if any')
    records_dir = migrate_records(conf_dir)

    print('This completes the configuration of the UChicago LDR Toolchain.')
    print('Please set the appropriate locations in your config file')
    for x in [(conf_dir, 'conf_dir'), (conf_file, 'conf_file'),
              (cvs_dir,'controlled_vocabs_dir'), (records_dir, 'records_dir')]:
        if not x[0]:
            continue
        else:
            print("{}: {}".format(x[1], x[0]))

if __name__ == '__main__':
    main()
