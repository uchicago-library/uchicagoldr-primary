from configparser import ConfigParser, SectionProxy
from inspect import getfile, getmodulename, getsourcefile
from os import access, mkdir, R_OK, W_OK
from os.path import abspath, dirname, expanduser, exists, isdir, join, realpath
import sys
from xdg import BaseDirectory


class LDRConfiguration(object):
    config_file = None
    data_file = None
    data = {}

    def __init__(self, config_directory=None):
        if config_directory and exists(abspath(config_directory)):
            if exists(join(config_directory, 'ldr.ini')):
                cfg_file = abspath(join(config_directory, 'ldr.ini'))
            else:
                raise ValueError('No config file exists in the ' +
                                 'specified directory')
        else:
            foundOne = False
            checkedDirs = []
            for directory in BaseDirectory.load_config_paths('ldr'):
                checkedDirs.append(directory)
                if exists(join(directory,'ldr.ini')):
                    foundOne = True
                    cfg_file = join(directory,'ldr.ini')
                    break
            if foundOne is False:
                raise ValueError('No config file was found in XDG config ' +
                                 'directories. The following directories ' +
                                 'were checked:\n{}'.format(
                                     '\n'.join(checkedDirs))
                                 )
        self.config_file = cfg_file
        self.data_file = self.retrieve_config_data()
        self.data = self.read_config_data()

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

    def retrieve_config_data(self):
        parser = ConfigParser()
        if exists(abspath(self.config_file)):
            parser.read(abspath(self.config_file))
        else:
            parser = self.write_config_data(parser)
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
