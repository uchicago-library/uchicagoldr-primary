from logging import getLogger, StreamHandler, Formatter, FileHandler
from logging.handlers import RotatingFileHandler
from fasteners import interprocess_locked
from os import makedirs
from os.path import join, expanduser, isdir
from tempfile import gettempdir
from uuid import uuid1

from uchicagoldrtoolsuite.core.lib.confreader import ConfReader
from uchicagoldrtoolsuite.core.lib.convenience import iso8601_dt


class MultiprocessRotatingFileHandler(RotatingFileHandler):
    @interprocess_locked(join(gettempdir(), 'ldrmasterlog.lock'))
    def emit(self, record):
        super().emit(record)
        self.close()


def spawn_logger(name, verbosity='DEBUG',
                 formatter=Formatter(
                     "[%(levelname)8s] [%(asctime)s] [%(name)s] = %(message)s",
                     datefmt="%Y-%m-%dT%H:%M:%S"
                 ),
                 handlers=[StreamHandler()]):
    rname = ''
    if master_log_name:
        rname = rname + master_log_name + "."
    rname = rname + name
    l = getLogger(rname)
    for x in handlers:
        x.setFormatter(formatter)
        x.setLevel(verbosity)
        l.addHandler(x)
    return l

f = Formatter("[%(levelname)8s] [%(asctime)s] [%(name)s] = %(message)s",
              datefmt="%Y-%m-%dT%H:%M:%S")
conf = ConfReader()
logdir = conf.get("Logging", "log_dir_path")
if logdir is None:
    logdir = join(expanduser("~"), 'ldrtslogs')
if not isdir(logdir):
    makedirs(logdir, exist_ok=True)
if not isdir(join(logdir, 'jobs')):
    makedirs(join(logdir, 'jobs'), exist_ok=True)
master_log_name = "ldrts"
master_log = getLogger(master_log_name)
master_log.setLevel('DEBUG')
h1 = MultiprocessRotatingFileHandler(join(logdir, master_log_name+".log"),
                                     maxBytes=200000000, backupCount=4)
h1.setFormatter(f)
master_log.addHandler(h1)
h2 = FileHandler(join(logdir, 'jobs', iso8601_dt() + "_" + uuid1().hex))
master_log.addHandler(h2)
