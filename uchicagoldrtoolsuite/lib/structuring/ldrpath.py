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
        if self.pipe:
            raise ValueError("file {} is already opened".format(self.item_name))
        else:
            self.pipe = open(self.item_name, 'ab') 
            return self.pipe
        
    def close(self):
        if not self.pipe:
            raise ValueError("file {} is alrady closed".format(self.item_name))
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