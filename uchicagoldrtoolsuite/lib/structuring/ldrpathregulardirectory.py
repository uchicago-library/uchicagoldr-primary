from pathlib import Path
from .abc.ldritem import LDRItem

class LDRPathRegularDirectory(LDRItem):

    def __init__(self, param1):
        self.item_name = param1
        self.path = Path(self.item_name)
        self.is_flo = False

    def open(self):
        return NotImplemented
    
    def read(self, blocksize):
        for n_thing in self.path.iterdir():
            if n_thing.is_file():
                with open(n_thing, 'rb') as f:
                    yield f.read(blocksize)
    
    def close(self):
        return NotImplemented
    
    def exists(self):
        return self.path.is_dir()
    
    def write(self):
        self.path.mkdir(parents=True)


    def pipe(self):
        return NotImplemented

    def is_flo(self):
        return False

    def item_name(self):
        return "hi"
