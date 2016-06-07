import csv

__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"

class DataFromCSV(object):
    def __init__(self):
        self.data = self.read_data('static/agents.csv')
    
    def read_data(self):
        fields = ['agentid','agentname']
        with open(self.filepath, 'r') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=fields, 
                                    delimiter=',', quotechar='"')
            self.data = reader
            
    def get_data(self):
        return self._data
    
    def set_data(self, value):
        if isinstance(value, dict) and len(value.keys()) > 0:
            self._data = value
        else:
            raise ValueError("DataFromCSV cannot have an " + 
                             "empty data attribute")
        
    data = property(get_data, set_data)
