from logging import getLogger, StreamHandler, Formatter, FileHandler
from logging.handlers import RotatingFileHandler
from fasteners import interprocess_locked
from os import makedirs
from os.path import join, expanduser, isdir
from tempfile import gettempdir
from uuid import uuid1

from uchicagoldrtoolsuite.core.lib.confreader import ConfReader
from uchicagoldrtoolsuite.core.lib.convenience import iso8601_dt

# Our master log, *all other logs should build off this*
#
# spawn_logger() provides a helper function for getting a properly formatted
# log into any other submodule of the toolsuite
# TODO: Probably read the master log name out of the conf, if possible
master_log_name = "ldrts"
master_log = getLogger(master_log_name)
master_log.setLevel('DEBUG')

# Our default log formatter, because its a hassle to have in multiple places
f = Formatter("[%(levelname)8s] [%(asctime)s] [%(name)s] = %(message)s",
              datefmt="%Y-%m-%dT%H:%M:%S")

conf = ConfReader()

class MultiprocessRotatingFileHandler(RotatingFileHandler):
    """
    Mix some fasteners in with stdlib logging, to avoid disasters in
    multipleprocesses writing to the same file via the master log
    """
    @interprocess_locked(join(gettempdir(), 'ldrmasterlog.lock'))
    def emit(self, record):
        super().emit(record)
        self.close()


def spawn_logger(name):
    """
    Spawn a log for a library component or an application.
    """
    rname = ''
    if master_log_name:
        rname = rname + master_log_name + "."
    rname = rname + name
    l = getLogger(rname)
    return l


def get_log_dir():
    """
    Try and get a directory the user wants the logs in.

    Otherwise put it in their home directory, because they'll probably
    get aggrovated they keep getting dumped there and search through
    the documentation to figure out how to fix that.
    """
    logdir = conf.get("Logging", "log_dir_path")
    if logdir is None:
        logdir = join(expanduser("~"), 'ldrtslogs')
    if not isdir(logdir):
        makedirs(logdir, exist_ok=True)
    if not isdir(join(logdir, 'jobs')):
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
        master_log.debug("Log size not specified in config. Setting to 1GB")
        max_log_size = 1000000000
    logdir = get_log_dir()
    mlog_filepath = join(logdir, master_log_name + ".log")
    h1 = MultiprocessRotatingFileHandler(mlog_filepath,
                                         maxBytes=int(max_log_size/5),
                                         backupCount=4)
    h1.setLevel(verbosity)
    h1.setFormatter(f)
    master_log.addHandler(h1)
    master_log.info("Now logging to master log file: " +
                    "{} @ {}".format(mlog_filepath, verbosity))


def activate_job_log_file(verbosity="DEBUG"):
    """
    Write a per job log file in $logdir/jobs with the filename of the time
    the job occured plus a uuid to not clobbering things
    """
    logdir = get_log_dir()
    jlog_filepath = join(logdir, 'jobs', iso8601_dt() + "_" + uuid1().hex)
    h2 = FileHandler(jlog_filepath)
    h2.setLevel(verbosity)
    h2.setFormatter(f)
    master_log.addHandler(h2)
    master_log.info("Now logging to job log file: "
                    "{} @ {}".format(jlog_filepath, verbosity))


def activate_stdout_log(verbosity="INFO"):
    h = StreamHandler()
    h.setLevel(verbosity)
    h.setFormatter(f)
    master_log.addHandler(h)
    master_log.info("Now logging to stdout @ {}".format(verbosity))
