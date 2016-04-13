
from abc import ABCMeta, abstractproperty

class Structure:
    
    __metaclass__ = ABCMeta
    
    @abstractmethod 
    def validate(self):
        if 
        raise NotImplemented
    
    def _validate(self):
        if getattr(self, 'required_parts', None):
            for n in self.required_parts:
                if not getattr(self, n, None):
                    return False
                elif not type(getattr(self, n, None)) == type(list):
                    return False
                return True
        else:
            return False
        
        def getrequiredparts(self):
            return self._required_parts
        
        def setrequiredparts(self, value):
            self._required_parts = value
            
        def getidentifier(self):
            return self._identifier
        
        def setidentifier(self, value):
            self._identifier = value
            
        required_parts = abstractproperty(getrequiredparts, setrequiredparts)
        identifier = abstractproperty(getidentifier, setidentifier)