class ValdationInterface(object):
    def __init__(self, v_type, data=None):
        self._validation_type  = v_type
        if data:
            self._data = data


    def set_validation_type(self, value):
        if not value in ['archiving', 'staging']:
            raise ValueError("invalid validation type specified")
        self._validation_type = value


    def get_validation_type(self):
        return self._validation_type


    def set_data(self, value):
        self._data = data


    def get_data(self):
        return self._data

    
    validation_type = property(get_validation_type, set_validation_type)
    data = property(get_data, set_data)
    
        
