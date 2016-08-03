from logging import getLogger, StreamHandler, Formatter

master_log_name = ''

master_log = getLogger(master_log_name)
master_log.setLevel('DEBUG')


#def spawn_logger(name, verbosity='INFO'):
def spawn_logger(name, verbosity='DEBUG',
                 formatter=Formatter(
                     "[%(levelname)8s] [%(asctime)s] [%(name)s] = " +
                     "%(message)s", datefmt="%Y-%m-%dT%H:%M:%S")):
    rname = ''
    if master_log_name:
        rname = rname + master_log_name + "."
    rname = rname + name
    l = getLogger(rname)
    h = StreamHandler()
    h.setFormatter(formatter)
    h.setLevel(verbosity)
    l.addHandler(h)
    return l
