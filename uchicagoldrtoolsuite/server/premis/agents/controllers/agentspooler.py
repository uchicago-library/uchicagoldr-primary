
from .datasourceselector import DataSourceSelector

class AgentSpooler(object):
    def __init__(self):
        self.data = DataSourceSelector('csv').get_data()
        self.