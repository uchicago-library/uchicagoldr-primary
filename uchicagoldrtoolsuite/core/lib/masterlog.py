from logging import getLogger, StreamHandler, Formatter

master_log_name = ''

master_log = getLogger(master_log_name)
master_log.setLevel('DEBUG')

f = Formatter("[%(levelname)8s] [%(asctime)s] [%(name)s] = " +
              "%(message)s",
              datefmt="%Y-%m-%dT%H:%M:%S")

h = StreamHandler()
h.setLevel('DEBUG')
h.setFormatter(f)

master_log.addHandler(h)

def spawn_logger(name):
    rname = ''
    if master_log_name:
        rname = rname + master_log_name + "."
    rname = rname + name
    return getLogger(rname)
