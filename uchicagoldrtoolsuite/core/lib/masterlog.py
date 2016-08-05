from logging import getLogger, StreamHandler, Formatter
from logging.handlers import RotatingFileHandler
from fasteners import interprocess_locked
from os.path import join, expanduser
from tempfile import gettempdir

from uchicagoldrtoolsuite.core.lib.confreader import ConfReader


class MultiprocessRotatingFileHandler(RotatingFileHandler):
    @interprocess_locked(join(gettempdir(), 'ldrmasterlog.lock'))
    def emit(self, record):
        super().emit(record)
        self.close()


def spawn_logger(name, verbosity='DEBUG', formatter=Formatter("[%(levelname)8s] [%(asctime)s] [%(name)s] = %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S"),
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
    logdir = expanduser("~")
master_log_name = "ldrts"
master_log = getLogger(master_log_name)
master_log.setLevel('DEBUG')
h = MultiprocessRotatingFileHandler(join(logdir, master_log_name+".log"),
                                    maxBytes=200000000, backupCount=4)
h.setFormatter(f)
master_log.addHandler(h)
