from .datafromcsv import DataFromCSV

__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class DataSourceSelector(object):
    def __init__(self, data_type):
        self.type_selection = data_type
        
    def get_data(self):
        choice = self.type_selection
        if choice == 'csv':
            return DataFromCSV()
        else:
            raise ValueError("wrong type selection")