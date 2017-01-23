from sys import exc_info
from os import makedirs
from os.path import join, expanduser, exists, dirname, isdir
from logging import getLogger, StreamHandler, Formatter, FileHandler
from logging.handlers import RotatingFileHandler
from tempfile import gettempdir
from functools import wraps
from uuid import uuid4
from logging import INFO

from pkg_resources import Requirement, resource_filename, resource_stream, \
    resource_string
from fasteners import interprocess_locked

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


# The default root logger
root_log = getLogger(__name__)
root_log.setLevel("DEBUG")

def liblog_filter(record, override_level=20):
    if record.levelno > override_level:
        return 1
    if ".lib." in record.name:
        return 0
    return 1

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
    logdir = join(expanduser("~"), '{}_logs'.format(__name__))
    return logdir


def activate_master_log_file(logdir=None, max_log_size=1000000000,
                             num_backups=4, verbosity="DEBUG"):
    """
    User our fancy subclass of RotatingFileHandler to write to a master
    log file safely from multiple processes
    """
    if logdir is None:
        logdir = get_log_dir()
    mlog_filepath = join(logdir, __name__ + ".log")
    if not isdir(dirname(mlog_filepath)):
        if exists(dirname(mlog_filepath)):
            raise ValueError('Logging dir would clobber something!')
        makedirs(dirname(mlog_filepath), exist_ok=True)
    h1 = MultiprocessRotatingFileHandler(mlog_filepath,
                                         maxBytes=int(max_log_size/5),
                                         backupCount=num_backups,
                                         encoding="UTF-8")
    h1.setLevel(verbosity)
    h1.setFormatter(_f)
    root_log.addHandler(h1)
    root_log.info("Now logging to master log file: " +
                  "{} @ {}".format(mlog_filepath, verbosity))


def activate_stdout_log(verbosity="INFO", filter_lib=True):
    h = StreamHandler()
    h.setLevel(verbosity)
    h.setFormatter(_f)
    if filter_lib:
        h.addFilter(liblog_filter)
    root_log.addHandler(h)
    root_log.info("Now logging to stdout @ {}".format(verbosity))


def activate_job_log_file(job_logdir=None, verbosity="DEBUG"):
    """
    Write a per job log file in $logdir/jobs with the filename of the time
    the job occured plus a uuid to not clobbering things
    """
    # Its kind of awkward to cram this import in this function definition, but I
    # dont think that the iso8601_dt() function really deserves to be at this
    # level of initialization unless its required.
    from uchicagoldrtoolsuite.core.lib.convenience import iso8601_dt
    if job_logdir is None:
        job_logdir = join(get_log_dir(), "jobs")
    makedirs(job_logdir, exist_ok=True)
    jlog_filepath = join(job_logdir, iso8601_dt() + "_" + uuid4().hex)
    if exists(jlog_filepath):
        raise ValueError('The randomly generated job log file already exists!')
    h2 = FileHandler(jlog_filepath)
    h2.setLevel(verbosity)
    h2.setFormatter(_f)
    root_log.addHandler(h2)
    root_log.info("Now logging to job log file: "
                  "{} @ {}".format(jlog_filepath, verbosity))


def clear_root_log_handlers():
    root_log.handlers = []

# Uncaught exception handling / Decorator


def handler(e, exc_info=None, log=None,
            log_exceptions=True, raise_exceptions=True):
    if log is None:
        log = root_log
    if log_exceptions:
        if raise_exceptions:
            log.exception(e, exc_info=exc_info)
        else:
            log.warning("BYPASSED EXCEPTION: {}".format(
                str(e)), exc_info=exc_info
            )
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
