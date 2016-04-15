
from abc import ABCMeta, abstractproperty, abstractmethod

class Structure(metaclass=ABCMeta):
        
    @abstractmethod 
    def validate(self):
        pass
    
    def _validate(self):
        for n_thing in self.required_parts:
            print(n_thing)
            if not getattr(self, n_thing, None):
                return False
            elif not isinstance(getattr(self, n_thing, None), list):
                return False
        return True
    

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
