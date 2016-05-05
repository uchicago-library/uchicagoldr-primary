from re import compile as re_compile

__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class DatabaseEnvironmentMixin(object):
    def set_db_ip(self, ip):
        if not isinstance(ip, str):
            raise ValueError('IPs must be provided as strings')
        ip_re = re_compile('^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')
        if not ip_re.match(ip):
            raise ValueError("{} doesn't look like a valid " +
                             "ip address.".format(ip))
        self._db_ip = ip

    def get_db_ip(self):
        return self._db_ip

    def set_db_port(self, port):
        if not isinstance(port, str):
            raise ValueError('Ports must be provided as strings')
        port_re = re_compile('^[\d]{1,}$')
        if not port_re.match(port):
            raise ValueError("{} doesn't like like a valid " +
                             "port number".format(port))
        self._db_port = port

    def get_db_port(self):
        return self._db_port

    def open_db_connection(self):
        pass

    def close_db_connection(self):
        pass

    property(get_db_ip, set_db_ip)
    property(get_db_port, set_db_port)
