from os.path import abspath, exists

class LDRPath(object):
    def __init__(self, param1):
        self.name = param1
        self.is_flo = True
        
    def read(self, blocksize=1024):
        with open(self.name,'rb') as f:
            bytes_data = f.read(blocksize)
            while len(bytes_data) > 0:
                bytes_data = f.read(blocksize)
        return bytes_data
    
    def open(self):
        return open(abspath(self.name, 'r'))
    
    def exists(self):
        return exists(abspath(self.name))
    
    def is_flo(self):
        return self.is_flo
    
    def write(self):
        return self.open()