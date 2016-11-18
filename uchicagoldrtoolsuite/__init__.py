from sys import exc_info
from os import makedirs
from os.path import join, isfile, expanduser
from logging import getLogger, StreamHandler, Formatter, FileHandler
from logging.handlers import RotatingFileHandler
from configparser import ConfigParser
from tempfile import gettempdir
from functools import wraps
from uuid import uuid4

from pkg_resources import Requirement, resource_filename, resource_stream, \
    resource_string
from fasteners import interprocess_locked
from xdg import BaseDirectory

# Initializes some key tools for working with the package structure, as well as
# configuring the global logger and the global config.


def retrieve_resource_filepath(resource_path, pkg_name=None):
    """
    retrieves the filepath of some package resource, extracting it if need be

    __Args__

    1. resource_path (str): The path to the resource in the package

    __KWArgs__

    * pkg_name (str): The name of a package. Defaults to the project name

    __Returns__

    * (str): The filepath to the resource
    """
    if pkg_name is None:
        pkg_name = __name__.split('.')[0]
    return resource_filename(Requirement.parse(pkg_name), resource_path)


def retrieve_resource_string(resource_path, pkg_name=None):
    """
    retrieves the string contents of some package resource

    __Args__

    1. resource_path (str): The path to the resource in the package

    __KWArgs__

    * pkg_name (str): The name of a package. Defaults to the project name

    __Returns__

    * (str): the resource contents
    """
    if pkg_name is None:
        pkg_name = __name__.split('.')[0]
    return resource_string(Requirement.parse(pkg_name), resource_path)


def retrieve_resource_stream(resource_path, pkg_name=None):
    """
    retrieves a stream of the contents of some package resource

    __Args__

    1. resource_path (str): The path to the resource in the package

    __KWArgs__

    * pkg_name (str): The name of a package. Defaults to the project name

    __Returns__

    * (io): an io stream
    """
    if pkg_name is None:
        pkg_name = __name__.split('.')[0]
    return resource_stream(Requirement.parse(pkg_name), resource_path)


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


def build_conf(config_directory=None, config_file=None,
               and_default=True, and_builtin=True):
    """
    Build a new ConfigParser from some standard spots

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
    paths = [x for x in paths if x is not None and isfile(x)]

    # Build a parser from each one
    subparsers = []
    for x in paths:
        subparser = ConfigParser()
        with open(x, 'r') as f:
            subparser.read_file(f)
        subparsers.append(subparser)

    # Build our master parser
    return mux_parsers(subparsers)


# The default global conf
conf = build_conf()

# The default root logger
root_log = getLogger(__name__)
root_log.setLevel("DEBUG")

# This mess is just a hassle to keep more than one place
_f = Formatter("[%(levelname)8s] [%(asctime)s] [%(name)s] = %(message)s",
               datefmt="%Y-%m-%dT%H:%M:%S")


class MultiprocessRotatingFileHandler(RotatingFileHandler):
    """
    Mix some fasteners in with stdlib logging, to avoid disasters in
    multipleprocesses writing to the same file via the root log
    """
    @interprocess_locked(join(gettempdir(), '{}_rootlog.lock'.format(__name__)))
    def emit(self, record):
        super().emit(record)
        self.close()


def get_log_dir():
    """
    Try and get a directory the user wants the logs in.

    Otherwise put it in their home directory, because they'll probably
    get aggrovated they keep getting dumped there and search through
    the documentation to figure out how to fix that.
    """
    try:
        logdir = conf.get("Logging", "log_dir_path")
    except:
        root_log.debug(
            "logdir not specified in the config. Setting to ~/ldrtslogs"
        )
        logdir = None
    if logdir is None:
        logdir = join(expanduser("~"), '{}_logs'.format(__name__))
    makedirs(join(logdir, 'jobs'), exist_ok=True)
    return logdir


def activate_master_log_file(verbosity="DEBUG"):
    """
    User our fancy subclass of RotatingFileHandler to write to a master
    log file safely from multiple processes
    """
    try:
        max_log_size = conf.getint("Logging", "max_size")
    except:
        root_log.debug("Log size not specified in config. Setting to 1GB")
        max_log_size = 1000000000
    try:
        num_backups = conf.getint("Logging", "num_backups")
    except:
        root_log.debug("Number of log backups to store not specified " +
                       "in config. Setting to 4")
        num_backups = 4
    logdir = get_log_dir()
    mlog_filepath = join(logdir, __name__ + ".log")
    h1 = MultiprocessRotatingFileHandler(mlog_filepath,
                                         maxBytes=int(max_log_size/5),
                                         backupCount=num_backups)
    h1.setLevel(verbosity)
    h1.setFormatter(_f)
    root_log.addHandler(h1)
    root_log.info("Now logging to master log file: " +
                  "{} @ {}".format(mlog_filepath, verbosity))


def activate_stdout_log(verbosity="INFO"):
    h = StreamHandler()
    h.setLevel(verbosity)
    h.setFormatter(_f)
    root_log.addHandler(h)
    root_log.info("Now logging to stdout @ {}".format(verbosity))


def activate_job_log_file(verbosity="DEBUG"):
    """
    Write a per job log file in $logdir/jobs with the filename of the time
    the job occured plus a uuid to not clobbering things
    """
    # Its kind of awkward to cram this import in this function definition, but I
    # dont think that the iso8601_dt() function really deserves to be at this
    # level of initialization unless its required.
    from uchicagoldrtoolsuite.core.lib.convenience import iso8601_dt
    logdir = get_log_dir()
    jlog_filepath = join(logdir, 'jobs', iso8601_dt() + "_" + uuid4().hex)
    h2 = FileHandler(jlog_filepath)
    h2.setLevel(verbosity)
    h2.setFormatter(_f)
    root_log.addHandler(h2)
    root_log.info("Now logging to job log file: "
                  "{} @ {}".format(jlog_filepath, verbosity))


def clear_root_log_handlers():
    root_log.handlers = []

# Uncaught exception handling / Decorators
# These are important because they're logging aware


def handler(e, exc_info=None, log=None,
            log_exceptions=True, raise_exceptions=True):
    if log is None:
        log = root_log
    if log_exceptions:
        if raise_exceptions:
            log.exception(e, exc_info=exc_info)
        else:
            log.warning("BYPASSED EXCEPTION: {}".format(str(e)), exc_info=exc_info)
    if raise_exceptions:
        raise(e)

def log_aware(log=None, raise_e=True):
    def _log_aware(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as e:
                handler(e, exc_info=exc_info(),
                        log=log, raise_exceptions=raise_e)
        return wrapper
    return _log_aware

#def log_aware(f):
#    @wraps(f)
#    def decorated_function(*args, **kwargs):
#        try:
#            return f(*args, **kwargs)
#        except Exception as e:
#            handler(e, exc_info=exc_info())
#    return decorated_function


#def log_aware_noraise(f):
#    # Probably don't use this, and instead try-catch the code itself explaining
#    # why its fine to not raise the exception.
#    @wraps(f)
#    def decorated_function(*args, **kwargs):
#        try:
#            return f(*args, **kwargs)
#        except Exception as e:
#            handler(e, exc_info=exc_info(), raise_exceptions=False)
#    return decorated_function
