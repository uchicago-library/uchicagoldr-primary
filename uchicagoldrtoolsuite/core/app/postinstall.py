from os.path import join
from shutil import copyfile

from xdg import BaseDirectory

from ..lib.convenience import retrieve_resource_filepath
from .internal.cliapp import CLIApp


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


def launch():
    app = PostInstall(
            __author__=__author__,
            __email__=__email__,
            __company__=__company__,
            __copyright__=__copyright__,
            __publication__=__publication__,
            __version__=__version__
    )
    app.main()


class PostInstall(CLIApp):
    def main(self):
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
        def_conf_dir = join(BaseDirectory.xdg_config_home, 'ldr')
        conf_dir = self.path_prompt("Where would you like your configuration " +
                                    "directory to be located?",
                                    default=def_conf_dir,
                                    must_be_absolute=True)
        if not conf_dir:
            self.stderrp('Invalid conf dir locaton specified')
            exit()
        assert(self.create_path('dir', conf_dir))
        print('We will now populate your configuration directory with some ' +
            'default files. Values set in your user config will override ' +
            'values in the global config. The global config is located ' +
            'inside of the python package. Changing them there and ' +
            'recompiling the package will set global defaults.')
        def_conf_file = join(conf_dir, 'ldr.ini')
        conf_file = self.path_prompt("Where would you like your primary ldr " +
                                     "configuration file located?",
                                     default=def_conf_file,
                                     must_be_absolute=True)
        if not conf_file:
            self.stderrp('Invalid conf file location specified')
            exit()
        assert(self.create_path('file', conf_file))
        copyfile(retrieve_resource_filepath('configs/ldr.ini', conf_file))
        print('For ease of editability we can provide you with user editable ' +
              'copies of the controlled vocabularies used by the ldr ' +
              'tool suite.')
        if self.bool_prompt('Would you like to copy these controlled ' +
                            'vocabularies into your config directory?',
                            default='y'):
            vocabs_list = ['controlledvocabs/filepaths_fits.json',
                           'controlledvocabs/filepaths_premis.json',
                           'controlledvocabs/filepaths_presform.json',
                           'controlledvocabs/restriction_codes.json']
            assert(self.create_path(join(conf_dir, 'controlledvocabs')))
            for x in vocabs_list:
                copyfile(retrieve_resource_filepath(x), join(conf_dir, x))
        print('For ease of editability we can provide you with user editable ' +
              'copies of record configurations used by the ldr tool suite.')
        if self.bool_prompt('Would you like to copy these record ' +
                            'configurations into your config directory?',
                            default='y'):
            record_configs_list = ['configs/AccessionRecordFields.csv']
            assert(self.create_path(join(conf_dir, 'record_configs')))
            for x in record_configs_list:
                copyfile(retrieve_resource_filepath(x), join(conf_dir, x))
        print("This completes the UChicago ldr tool suite post install process.")
