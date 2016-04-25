from requests import get as rget
from requests import codes
from requests import head as rhead
from tempfile import TemporaryDirectory
from os.path import join
from uuid import uuid1
from .abc.ldritem import LDRItem

class LDRURL(LDRItem):
    def __init__(self, param1):

        self.item_name = param1
        self.pipe = None
        self.tmpdir = None
        self.is_flo = True

    def read(self, blocksize=1024):
        if not self.pipe:
            raise OSError('{} not open for reading'.format(str(self.item_name)))
        return self.pipe.read(blocksize)

    def write(self, data):
        raise OSError('URLs are read only.')

    def open(self, mode='rb', buffering=-1, errors=None):
        if "t" in mode:
            raise OSError('LDR Items do not support text mode')
        if mode == 'r' or \
                mode == 'w' or \
                mode == 'a':
            mode = mode + "b"
        if buffering < 1:
            buffering = 1024
        r = rget(self.item_name, stream=True)
        self.tmpdir = TemporaryDirectory()
        tmpfile_name = join(self.tmpdir.name, str(uuid1()))
        with open(tmpfile_name, 'wb') as tmpfile:
            for chunk in r.iter_content(chunk_size=buffering):
                if chunk:
                    tmpfile.write(chunk)
        self.pipe = open(tmpfile_name, mode=mode,
                         buffering=buffering, errors=errors)
        return self

    def close(self):
        if not self.pipe:
            raise ValueError("file {} is already closed".format(self.item_name))
        else:
            self.pipe.close()
            self.pipe = None
            if self.tmpdir:
                self.tmpdir.cleanup()
                self.tmpdir = None

    def exists(self):
        r = rhead(self.item_name)
        return r.status_code == codes.ok

