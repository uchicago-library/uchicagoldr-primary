from pathlib import Path
from .abc.ldritem import LDRItem


class LDRPathRegularFile(LDRItem):
    def __init__(self, param1):
        self.item_name = param1
        self.path = Path(self.item_name)
        self.pipe = None
        self.is_flo = True

    def read(self, blocksize=1024):
        if not self.pipe:
            raise OSError('{} not open for reading'.format(str(self.path)))
        return self.pipe.read(blocksize)

    def open(self, mode='rb', buffering=-1, errors=None):
        if "t" in mode:
            raise OSError('LDR Items do not support text mode')
        if mode == 'r' or \
                mode == 'w' or \
                mode == 'a':
            mode = mode + "b"
        self.pipe = open(str(self.path), mode=mode,
                         buffering=buffering, errors=errors)
        return self

    def close(self):
        if not self.pipe:
            raise ValueError("file {} is already closed".format(self.item_name))
        else:
            self.pipe.close()
            self.pipe = None

    def exists(self):
        return self.path.exists()

    def write(self, data):
        if self.pipe:
            print(self.pipe)
            self.pipe.write(data)
            return True
        else:
            raise ValueError("file {} is not opened and " +
                             "therefore cannot write".format(self.item_name))
