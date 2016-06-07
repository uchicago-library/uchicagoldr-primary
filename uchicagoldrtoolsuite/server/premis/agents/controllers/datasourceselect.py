
class DataSourceSelect(object):
    def __init__(self, data_type):
        self.type_selection = data_type
        
    def get_data(self):
        choice = self.type_selection
        if choice == 'csv':
            return DataFromCSV()
        else:
            raise ValueError("wrong type selection")