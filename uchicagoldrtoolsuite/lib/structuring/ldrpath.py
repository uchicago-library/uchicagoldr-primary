from os.path import abspath, exists

class LDRPath(object):
    def __init__(self, param1):
        self.item_name = param1
        self.is_flo = True
        
    def read(self, blocksize=1024):
        with open(self.name,'rb') as f:
            bytes_data = f.read(blocksize)
            while len(bytes_data) > 0:
                yield bytes_data
                bytes_data = f.read(blocksize)

    def open(self):
        return open(abspath(self.name, 'r'))
        
    def exists(self):
        return exists(abspath(self.name))
    
    def write(self):
        return self.open()