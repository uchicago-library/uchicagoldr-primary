import csv

class DataFromCSV(object):
    def __init__(self):
        self.filepath = 'agents.csv'
        
    def read_data(self):
        fields = ['agentid','agentname']
        with open(self.filepath, 'r') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=fields, 
                                    delimiter=',', quotechar='"')
            self.data = reader