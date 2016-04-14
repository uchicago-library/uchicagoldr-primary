
from .internals.ldrpath import LDRPath

class LDRPathRegularDirectory(LDRPath):

    def __init__(self, param1):
        super().init__(param1)
        self.is_flo = False
        
    def open(self):
        return NotImplemented
    
    def read_bytes(self, blocksize):
        return self.path.iterdir()
    
    def close(self):
        return NotImplemented
    
    def exists(self):
        return self.path.is_dir()
    
    def write(self):
        self.path.mkdir(parents=False)