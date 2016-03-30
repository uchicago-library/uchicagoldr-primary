from configparser import ConfigParser
from inspect import getfile
from os import access, mkdir, R_OK, W_OK
from os.path import abspath, exists, join
from xdg import BaseDirectory


class LDRConfiguration(object):
    config_file = None
    config_dir = None
    data_file = None
    data = {}

    def __init__(self, config_directory=None, config_file=None):
        if config_directory is None:
            self.config_dir = self.find_config_dir()
        else:
            self.config_dir = config_directory
#        # Handle a conf dir not existing
#        if self.config_dir is None:
#            self.spawn_config_dir(self.hypothesize_config_dir_loc())
        if not exists(self.config_dir):
            raise ValueError("The config dir does not exist")

        if config_file is None:
            self.config_file = 'ldr.ini'
        else:
            self.config_file = config_file
        self.config_file_fullpath = join(self.config_dir, self.config_file)
#        # Handle a conf file not existing
        if not exists(self.config_file_fullpath):
#            self.spawn_config_file(self.config_file_fullpath)
#            raise ValueError('A new config file with default values ' +
#                             'has been created at {}.\n'.format(
#                                 self.config_file_fullpath) +
#                             'Please populate it with appropriate values.')
            raise ValueError("The primary config file doesn't exist")

        self.data_file = self.retrieve_config_data()
        self.data = self.read_config_data()

    def find_config_dir(self):
        conf_dir = [x for x in BaseDirectory.load_config_paths('ldr')]
        if conf_dir:
            return conf_dir[0]
        else:
            return None

    def hypothesize_config_dir_loc(self):
        return join(BaseDirectory.xdg_conf_dirs[0], 'ldr')

    def find_config_sections(self):
        output = []
        for n in self.data:
            output.append(n)
        return output

    def read_a_config_section(self, sname):
        output = []
        if self.data.get(sname):
            for n in self.data.get(sname):
                output.append(n)
        else:
            return ValueError("there is no {} section in the configuration data".format(sname))
        return output

    def get_a_config_data_value(self, sname, data_element):
        if not self.data.get(sname):
            return ValueError("there is no {} section".format(sname))
        elif not self.data.get(sname).get(data_element):
            return ValueError("there is no {} data element".format(data_element))
        else:
            return self.data.get(sname).get(data_element)

    def write_config_data(self, p):
        assert isinstance(p, ConfigParser)
        p.add_section('Database')
        p.add_section('Logging')
        p.set('Database','db_host','example.com')
        p.set('Database','db_name','fill_me_in')
        p.set('Database','db_user','fill_me_in_with_something_real')
        p.set('Database','db_pass','replace_me')
        p.set('Logging','server','example.com')
        p.set('Logging','port','1')
        return p

    def spawn_config_dir(self, loc):
        makedirs(loc)
        makedirs(join(loc, 'controlled_vocabularies'))
        makedirs(join(loc, 'record_configurations'))

    def spawn_config_file(self, loc):
        p = ConfigParser()
        p.add_section('Database')
        p.add_section('Logging')
        p.add_section('Paths')
        p.set('Database','db_host','DB_HOSTNAME_OR_IP_HERE')
        p.set('Database','db_name','DB_NAME_HERE')
        p.set('Database','db_user','DB_USERNAME_HERE')
        p.set('Database','db_pass','DB_USER_PASSWORD_HERE')
        p.set('Logging','server','LOGGING_HOSTNAME_OR_IP_HERE')
        p.set('Logging','port','LOGGING_PORT_#_HERE')
        p.set('Paths', 'staging_root', 'STAGING_ROOT_PATH_HERE')
        p.set('Paths', 'archive_root', 'ARCHIVE_ROOT_PATH_HERE')
        p.set('Paths', 'controlled_vocabularies',
              join(self.config_dir, 'controlled_vocabularies'))
        p.set('Paths', 'record_configurations',
              join(self.config_dir, 'record_configurations'))
        with open(loc, 'w') as f:
            p.write(f, space_around_delimiters=True)


    def spawn_config_parser(self):
        pass

    def retrieve_config_data(self):
        parser = ConfigParser()
        if exists(abspath(self.config_file_fullpath)):
            parser.read(abspath(self.config_file_fullpath))
        else:
#            parser = self.write_config_data(parser)
            raise ValueError()
            cfgfile = open(join(abspath(self.config_file)),'w')
            parser.write(cfgfile)
            cfgfile.close()
        return parser

    def read_config_data(self):
        out = {}
        for n in self.data_file:
            out[n.lower()] = {}
            for p in self.data_file[n]:
                p = p.lower()
                out[n.lower()][p.lower()] = self.data_file[n][p]
        return out
