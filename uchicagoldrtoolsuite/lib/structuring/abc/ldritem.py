'''
Created on Apr 13, 2016

@author: tdanstrom
'''

class LDRItem:
    name = ""
    is_flo = True
    
    def read(self, blocksize):
        raise NotImplemented()
    
    def write(self):
        raise NotImplemented()
    
    def open(self):
        raise NotImplemented
    
    def close(self):
        raise NotImplemented()
    
    def is_flo(self):
        raise NotImplemented()
    
    def exists(self):
        raise NotImplemented()