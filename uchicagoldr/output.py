
from uchicagldrconfig.LDRConfiguration import LDRConfiguration

config = LDRConfiguration("C:\Users\tdanstrom\Documents\source_code\ldr_configuraton").get_config()

class LDRError(object):
    source = None
    label = ""
    message = ""

    def __init__(self, exception):
        assert isinstance(exception, Exception)
        self.source = exception
        self.label = exception.__name__
        self.message = exception.__message__
    
    def get_label(self):
        return self.label

    def get_message(self):
        return self.message
        

class Output(object):
    status = False
    error = None
    data  = None

    def __init_(self, type_string):
        if type_string in config['outputinformation']['valid_types']
            self.type = type_string
        else:
            self.type = None
        self.data = None

    def add_error(self, error_object):
        if self.error != None:
            return -1
        elif not isinstance(error_object, LDRError):
            return -1
        else:
            self.error = error_object
    
    def get_error(self):
        if self.error != None:
            return "{0}: {1}".format(self.error.get_label(),
                                     self.error.get_message())
    def get_status(self):
        return self.status

    def get_data(self):
        return self.data

    def add_data(self, data_object):
        if self.type != None data_object.__name__.lower() == self.type:
            self.data = data_object
            return 0
        else:
            return -1

    def display(self, record_format):
        if record_format in config['output_information']['valid_formats']:
            command = 'to_'+record_format
            return getattr(self.data.get_data(),command)()
            
