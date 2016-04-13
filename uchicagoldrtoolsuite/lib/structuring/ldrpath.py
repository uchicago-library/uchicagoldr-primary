from os.path import abspath, exists
from pathlib import Path

class LDRPath(object):
    def __init__(self, param1):
        self.item_name = param1
        self.path = Path(param1)
        self.pipe = None
        self.is_flo = True if self.path.is_file() else False
        
    def read(self, blocksize=1024):
        with self.path.open('rb'):
            bytes_data = self.path.read_bytes(blocksize)
            while len(bytes_data) > 0:
                yield bytes_data
                bytes_data = self.path.read_bytes(blocksize)

    def open(self):
        return self.path.open('ab')
        
    def close(self):
        if not self.pipe:
            raise ValueError("file {} is already closed".format(self.item_name))
        else:
            self.pipe.close()
            self.pipe = None
        
    def exists(self):
        return exists(abspath(self.name))
    
    def write(self, data):
        if self.pipe:
            self.pipe.write(data)
            return True
        else:
            raise ValueError("file {} is not opened and therefore cannot write".format(self.item_name))