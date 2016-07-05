from os import remove
from os.path import getsize
from pathlib import Path

from .abc.ldritem import LDRItem


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class LDRPath(LDRItem):
    """
    Allows a file path to a file on the file system to be treated as an LDRItem
    """
    def __init__(self, param1, root=None):
        self.path = Path(param1)
        if root is None:
            self.item_name = str(self.path)
        else:
            self.item_name = str(self.path.relative_to(root))
        self.pipe = None
        self.is_flo = True

    def read(self, blocksize=1024*1000*100):
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

    def delete(self, final=False):
        if final:
            if self.exists():
                remove(str(self.path))
            if not self.exists():
                return (True, "{} no longer exists.".format(self.item_name))
            else:
                return (False, "{} exists.".format(self.item_name))
        else:
            return (False, "{} will be removed.".format(self.item_name))

    def write(self, data):
        if self.pipe:
            self.pipe.write(data)
            return True
        else:
            raise ValueError("file {} is not opened and " +
                             "therefore cannot write".format(self.item_name))
    def get_size(self, buffering=1024*1000*100):
        """
        Overwrite LDRItem.get_size(), because this is faster.

        Preserve the buffering kwarg for compatability, even though
        we don't use it for anything
        """
        if self.exists():
            return self.path.stat().st_size
        else:
            return 0
