from os import remove
from pathlib import Path
from json import dumps
from logging import getLogger

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, \
    log_init_success
from .abc.ldritem import LDRItem


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class LDRPath(LDRItem):
    """
    Allows a file path to a file on the file system to be treated as an LDRItem
    """
    @log_aware(log)
    def __init__(self, param1, root=None):
        """
        Creates a new LDRPath.

        __Args__

        1. param1 (str/bytes): A path to a location on disk

        __KWArgs__

        * root (type(param1)): A root to take the provided path relative to
            for documentation/naming purposes
        """
        log_init_attempt(self, log, locals())
        self.path = Path(param1)
        if root is None:
            self.item_name = str(self.path)
        else:
            self.item_name = str(self.path.relative_to(root))
        self.pipe = None
        self.is_flo = True
        log_init_success(self, log)

    @log_aware(log)
    def __repr__(self):
        attrib_dict = {
            'item_name': self.item_name,
            'path': str(self.path)
        }
        return "<LDRPath {}>".format(dumps(attrib_dict, sort_keys=True))

    @log_aware(log)
    def read(self, blocksize=1024*1000*100):
        """
        Read from an opened LDRPath

        __KWArgs__

        * blocksize (int): how many bits to read in one go

        __Returns__

        (bytes): The read data
        """
        if not self.pipe:
            raise OSError('{} not open for reading'.format(str(self.path)))
        return self.pipe.read(blocksize)

    @log_aware(log)
    def open(self, mode='rb', buffering=-1, errors=None):
        """
        Opens the LDRPath in the specified mode.

        __KWArgs__

        * see python open() documentation

        __Returns__

        * self (opened)
        """
        log.debug(
            "{} opened. Mode: {}. Buffering {}".format(
                str(self), mode, str(buffering)
            )
        )
        if "t" in mode:
            raise OSError('LDR Items do not support text mode')
        if mode == 'r' or \
                mode == 'w' or \
                mode == 'a':
            mode = mode + "b"
        self.pipe = open(str(self.path), mode=mode,
                         buffering=buffering, errors=errors)
        return self

    @log_aware(log)
    def close(self):
        """
        Closes the LDRPath
        """
        log.debug("{} closed".format(str(self)))
        if not self.pipe:
            raise ValueError("file {} is already closed".format(self.item_name))
        else:
            self.pipe.close()
            self.pipe = None

    @log_aware(log)
    def exists(self):
        """
        Tests whether the location the LDRPath is pointed at already exists

        __Returns__

        * (bool): True if it exists, false if it doesn't
        """
        log.debug("{} existence checked".format(str(self)))
        return self.path.exists()

    @log_aware(log)
    def delete(self, final=False):
        """
        DELETES THE FILE AT THE LDRPATH'S LOCATION FROM DISK

        __KWArgs__

        * final (bool): If not true perform a mock-delete, otherwise
            removes the thing at the LDRPath's location from disk


        __Returns__

        * (tuple (bool, str)): A tuple containing deletion results and a short
            explanatory string. True == File Deleted, False == Not deleted.
        """
        if final:
            log.debug("{} deleted".format(str(self)))
            if self.exists():
                remove(str(self.path))
            if not self.exists():
                return (True, "{} no longer exists.".format(self.item_name))
            else:
                return (False, "{} exists.".format(self.item_name))
        else:
            log.debug("{} pseudo-deleted".format(str(self)))
            return (False, "{} will be removed.".format(self.item_name))

    @log_aware(log)
    def write(self, data):
        """
        Write data into the LDRPath's location

        __Args__

        1. data (bytes): data to write to the location
        """
        if self.pipe:
            self.pipe.write(data)
            return True
        else:
            raise ValueError("file {} is not opened and " +
                             "therefore cannot write".format(self.item_name))

    @log_aware(log)
    def get_size(self, buffering=1024*1000*100):
        """
        Overwrite LDRItem.get_size(), because this is faster.

        Preserve the buffering kwarg for compatability, even though
        we don't use it for anything

        __KWArgs__

        * buffering (*): ignored in this implementation

        __Returns__

        * (int): The size of the file at the location, or 0 if nothing exists or
            there is no data written at the location.
        """
        log.debug("{} size checked".format(str(self)))
        if self.exists():
            return self.path.stat().st_size
        else:
            return 0
